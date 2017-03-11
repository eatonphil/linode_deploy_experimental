## Getting started

* [Create an API key](https://www.linode.com/docs/platform/api/api-key)
  * Put it in ~/.linode_v3.token
* [Install python-linode-apiv3](https://github.com/eatonphil/python-linode-apiv3)

## Supported images:

* freebsd-11-0
* openbsd-6-0

## Usage:

```sh
$ LINODE_APIV3_KEY=$(cat ~/.linode_v3.token) python3 deploy.py --help
usage: deploy.py [-h] [-b] [-n] [-d] image

positional arguments:
  image                 must supply an image. Options are [freebsd-11-0,
                        openbsd-6-0]

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
$ LINODE_APIV3_KEY=$(cat ~/.linode_v3.token) python3 deploy.py freebsd-11-0
```