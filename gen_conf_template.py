#!/usr/bin/env python

import sys

from config_parser import OSConfigParser, print_comments, show_header, \
                          format_var_name, value_to_yaml, infer_type


def print_ini_jinja(parser, prefix, namespace):
    values = parser.values

    for section in values:
        print '\n[{0}]\n'.format(section)

        if len(values[section]['comments']) > 0:
            print_comments(values[section]['comments'], newline=1)

        for name, entry in values[section]['entries'].iteritems():
            if len(entry['comments']) > 0:
                print_comments(entry['comments'])

            value = value_to_yaml(entry)
            value_type = infer_type(entry['comments'])

            var_name = name

            section = format_var_name(section)

            if section.lower() != 'default':
                var_name = "{0}_{1}".format(section.lower(), var_name)

            if namespace and not var_name.startswith(namespace):
                var_name = "{0}_{1}".format(namespace, var_name)

            if prefix:
                var_name = "{0}_{1}".format(prefix, var_name)

            var_name = format_var_name(var_name)

            # if entry['commented'] and val is None:
            if value_type in ['int', 'multi', 'bool']:
                print "{{% if {0} is none -%}}#{{%- endif -%}}".format(var_name)
            elif value_type in ['str', 'list', None] or value is None:
                print "{{% if not {0} -%}}#{{%- endif -%}}".format(var_name)
                
            if value_type == 'multi':
                print ("{{% if {1} is sequence %}}"
                       "{{% for val in {0} %}}"
                       "{0}={{{{ item }}}}"
                       "{{% endfor %}}"
                       "{{% else %}}"
                       "{0}={{{{ {1} }}}}"
                       "{{% endif %}}\n".format(name, var_name))
            else:
                print "{0}={{{{ {1} }}}}\n".format(name, var_name)

    # custom section configs
    print """
#
# Custom section configs
#
{%% for section, keypair in %s | dictsort %%}
[{{ section }}]
{%% if keypair is not string %%}
{%% for name, value in keypair | dictsort %%}
{{ name }}={{ value }}
{%% endfor %%}
{%% endif %%}
{%% endfor %%}""" % "{0}_{1}".format(prefix, namespace)


if __name__ == '__main__':
    fpath = sys.argv[1]
    namespace = sys.argv[2] if len(sys.argv) >= 3 else ''
    prefix = sys.argv[3] if len(sys.argv) >= 4 else ''
    desc = sys.argv[4] if len(sys.argv) >= 5 else ''

    parser = OSConfigParser()
    with open(fpath) as f:
        lines = [line.strip() for line in f.readlines()]
        parser.parse(lines)

        show_header(fpath, namespace, prefix, desc, yaml=False)

        print_ini_jinja(parser, prefix=prefix, namespace=namespace)
