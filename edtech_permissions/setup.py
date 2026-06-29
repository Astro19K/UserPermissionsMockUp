from setuptools import setup, find_packages

setup(
    name='edtech_permissions',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django>=3.2',
    ],
    entry_points={
        "lms.djangoapp": [
            "edtech_permissions = edtech_permissions.apps:EdtechPermissionsConfig",
        ],
        "cms.djangoapp": [
            "edtech_permissions = edtech_permissions.apps:EdtechPermissionsConfig",
        ],
    },
)
