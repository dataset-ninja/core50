Dataset **CORE50** can be downloaded in [Supervisely format](https://developer.supervisely.com/api-references/supervisely-annotation-json-format):

 [Download](https://assets.supervisely.com/supervisely-supervisely-assets-public/teams_storage/B/Q/a4/2ULAjDGFje3eU5YcubxYOhToQxZGRrJdAh9u8G7KmajpWiW2I1QYmKuapV7VjMJYgcPgFqjF5sXaj3VZNTdFsieaxBEU5SddBLFNsCWAiPhHIfxpn1TlEr1ifcKm.tar)

As an alternative, it can be downloaded with *dataset-tools* package:
``` bash
pip install --upgrade dataset-tools
```

... using following python code:
``` python
import dataset_tools as dtools

dtools.download(dataset='CORE50', dst_dir='~/dataset-ninja/')
```
Make sure not to overlook the [python code example](https://developer.supervisely.com/getting-started/python-sdk-tutorials/iterate-over-a-local-project) available on the Supervisely Developer Portal. It will give you a clear idea of how to effortlessly work with the downloaded dataset.

The data in original format can be downloaded here:

- [full-size_350x350_images.zip](http://bias.csr.unibo.it/maltoni/download/core50/core50_350x350.zip)
- [bbox.zip](https://vlomonaco.github.io/core50/data/bbox.zip)
- [full-size_350x350_depth.zip](http://bias.csr.unibo.it/maltoni/download/core50/core50_350x350_depth.zip)
- [core50_train.csv](https://vlomonaco.github.io/core50/data/core50_train.csv)
- [core50_test.csv](https://vlomonaco.github.io/core50/data/core50_test.csv)
