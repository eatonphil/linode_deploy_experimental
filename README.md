## Installation

First, [create an API key](https://www.linode.com/docs/platform/api/api-key).

Then, grab the script and its dependencies:

```bash
$ pip3 install linode_deploy_experimental
```

Set LINODE_APIV3_KEY in your .bashrc or .profile so you don't
need to specify it each time you run the script.

## Usage:

```sh
$ linode_deploy_experimental --help
usage: deploy.py [-h] [-b] [-n] [-d] image

positional arguments:
  image                 must supply an image. Options are [freebsd-11-0,
                        openbsd-6-0, netbsd-7-1, centos-7-0]

optional arguments:
  -h, --help            show this help message and exit
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
$ linode_deploy_experimental freebsd-11-0 -bd
```

## Supported images:

* freebsd-11-0 (ufs)
* openbsd-6-0
* netbsd-7-1
* centos-7-0 (xfs)
