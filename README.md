## Installation

First, [create an API key](https://www.linode.com/docs/platform/api/api-key).

Then, grab the script and its dependencies:

```bash
$ pip3 install linode_deploy_experimental
```

NOTE: some distributions may require you to explicitly install the TCL `expect` program.

Set LINODE_APIV3_KEY in your .bashrc or .profile so you don't
need to specify it each time you run the script.

## Usage:

```sh
$ linode_deploy_experimental --help
usage: linode_deploy_experimental [-h] [--api_key API_KEY] [-b] [-n] [-d]
                                  image

positional arguments:
  image                 must supply an image. Options are [freebsd-11-0,
                        openbsd-6-0, netbsd-7-1, centos-7-0]

optional arguments:
  -h, --help            show this help message and exit
  --api_key API_KEY     your APIv3 key must be supplied.
  -b, --boot-immediately
                        Boots immediately into the image after install with an
                        unsafe password
  -n, --no-cleanup      Prevent temporary disks and configs from being deleted
  -d, --delete-on-failure
                        Automatically deletes the created Linode on script
                        failure
```

### Example:

```sh
$ linode_deploy_experimental freebsd-11-0 -bd --api_key $(cat ~/.linode_v3.token)
```

## Supported images:

* freebsd-11-0 (ufs)
* openbsd-6-0
* netbsd-7-1
* centos-7-0 (xfs)
