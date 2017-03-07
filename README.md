## Getting started

* [Create an API key](https://www.linode.com/docs/platform/api/api-key)
  * Put it in ~/.linode_v3.token
* [Install python-linode-apiv3](https://github.com/eatonphil/python-linode-apiv3)

## Supported images:

* freebsd-11-0
* openbsd-6-0

## Usage:

```
LINODE_APIV3_KEY=$(cat ~/.linode_v3.token) python3 deploy.py freebsd-11-0 foo123 bar123
```

Note: the current password for an image is `password123`. This needs to changed sometime.