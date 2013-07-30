#!/usr/bin/env python


def check_new_version_on_pypi():
    import xmlrpclib, pip
    import argparse
    from pkg_resources import parse_version
    
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-a', '--all', dest='all', action='store_true', default=False)
    parser.add_argument('-m', '--mirror', dest='mirror', default='http://pypi.python.org/pypi')
    args = parser.parse_args()
    pypi = xmlrpclib.ServerProxy(args.mirror)
    
    def print_status(package, message):
        package_str = 'package: {package.project_name} {package.version}'.format(package=package)
        print '{package:30} {message}'.format(package=package_str, message=message)
        
    
    for local in pip.get_installed_distributions():
        available = pypi.package_releases(local.project_name)
        if available:
            if local.project_name == 'pyserial':
                # compare local and remote versions
                comparison = cmp(parse_version(available[0]), parse_version(local.version))
                if comparison == 0:
                    if not args.all:
                        continue
                    print_status(local, 'Up to date')
                elif comparison < 0:
                    print_status(local, 'Older version on pypi')
                else:
                    print_status(local, 'Version %s available on PyPI' % available[0])
                    print 'You should upgrade'
                return 0

    return 0
    
if __name__ == '__main__':
    check_new_version_on_pypi()







