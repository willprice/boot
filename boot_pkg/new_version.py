import xmlrpclib, pip
from pkg_resources import parse_version

# check for new versions of "boot" on the Pypi server.
# this function just return suggestions
def check_on_pypi():

    import argparse

    parser = argparse.ArgumentParser(description='Process some integers.')

    parser.add_argument('-a', '--all', dest='all', action='store_true', 
                        default=False)

    parser.add_argument('-m', '--mirror', dest='mirror', 
                        default='http://pypi.python.org/pypi')

    args = parser.parse_args()
    pypi = xmlrpclib.ServerProxy(args.mirror)
    
    for local in pip.get_installed_distributions():
        # search for "boot" locally installed
        if local.project_name == 'boot':
            try:
                # search for "boot" remotely on Pypi 
                available = pypi.package_releases(local.project_name)
            except:
                return 'Problems in checking the pypi server. '+\
                       'Maybe the connection is down.'
            if available:
                # compare local and remote versions
                comparison = cmp(parse_version(available[0]), 
                                 parse_version(local.version))

                if comparison == 0:
                    return 'Current version of "boot" is '+ local.version + \
                           ' and it is the newest version.'

                elif comparison < 0:
                    return 'Pypi server has an older version of "boot".'

                # new version available for download
                else:
                    return 'Newer version found.\n'+\
                      'Run the terminal command: sudo pip install --upgrade boot'
            else:
                return 'No package named "boot" is found on pypi servers.'

    return 'No package named "boot" installed in your machine.\n'+\
           'Run the terminal command: sudo pip install boot'
   

