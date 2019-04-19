from setuptools import setup

setup(
    name='protfarm-gui',
    version='0.1.0',
    url='https://github.com/GradinaruLab/protfarm-gui',
    author='David Brown',
    author_email='dibidave@gmail.com',
    packages=[
        "protfarm_gui",
    ],
    python_requires='~=3.6',
    entry_points={
        "console_scripts": [
            "protfarm-gui=protfarm_gui.launcher:launch"
        ]
    },
    install_requires=[
        "numpy",
        "matplotlib",
        "seaborn",
        "protfarm",
        "pepars"
    ]

)
