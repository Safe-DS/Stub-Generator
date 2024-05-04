## [0.3.0](https://github.com/Safe-DS/Stub-Generator/compare/v0.2.0...v0.3.0) (2024-05-04)


### Features

* Added handling for sequence classes ([#127](https://github.com/Safe-DS/Stub-Generator/issues/127)) ([cb061ab](https://github.com/Safe-DS/Stub-Generator/commit/cb061ab5e2ca10f9a8270d4141d6ac842612920e)), closes [#126](https://github.com/Safe-DS/Stub-Generator/issues/126)
* DocString result names for Safe-DS stub results ([#101](https://github.com/Safe-DS/Stub-Generator/issues/101)) ([fe163e3](https://github.com/Safe-DS/Stub-Generator/commit/fe163e30b7a22b638d5aa6a2f861221afd2fc79c)), closes [#100](https://github.com/Safe-DS/Stub-Generator/issues/100)
* Examples from docstrings are also taken over to stub docstrings ([#116](https://github.com/Safe-DS/Stub-Generator/issues/116)) ([6665186](https://github.com/Safe-DS/Stub-Generator/commit/6665186badeb10580081544603ce82878760fbfc)), closes [#115](https://github.com/Safe-DS/Stub-Generator/issues/115)
* Replace the docstring_parser library with Griffe ([#79](https://github.com/Safe-DS/Stub-Generator/issues/79)) ([9b2f802](https://github.com/Safe-DS/Stub-Generator/commit/9b2f802311f51befbe5df2e54deadced84c372a6))


### Bug Fixes

* `Self` types as results are translated to class names  ([#110](https://github.com/Safe-DS/Stub-Generator/issues/110)) ([4554a56](https://github.com/Safe-DS/Stub-Generator/commit/4554a5637f441490f513b09ccc411c1c13d14d15)), closes [#86](https://github.com/Safe-DS/Stub-Generator/issues/86)
* Creating stubs with relative paths for source and output directories ([#128](https://github.com/Safe-DS/Stub-Generator/issues/128)) ([b4493c9](https://github.com/Safe-DS/Stub-Generator/commit/b4493c90e29a9eabc0d28167982ab44172040961)), closes [#125](https://github.com/Safe-DS/Stub-Generator/issues/125)
* Docstrings have the correct indentation for nested classes (stubs) ([#114](https://github.com/Safe-DS/Stub-Generator/issues/114)) ([c7b8550](https://github.com/Safe-DS/Stub-Generator/commit/c7b8550af78e87cdec989ce0b11db6e984bb7e21)), closes [#113](https://github.com/Safe-DS/Stub-Generator/issues/113)
* Fixed a bug where double ? would be generated for stubs ([#103](https://github.com/Safe-DS/Stub-Generator/issues/103)) ([c35c6ac](https://github.com/Safe-DS/Stub-Generator/commit/c35c6ac4d6beae253da66b7acb1d91093023481c)), closes [#87](https://github.com/Safe-DS/Stub-Generator/issues/87) [#87](https://github.com/Safe-DS/Stub-Generator/issues/87)
* Fixed a bug where imports would not check reexports for shortest path ([#112](https://github.com/Safe-DS/Stub-Generator/issues/112)) ([48c5367](https://github.com/Safe-DS/Stub-Generator/commit/48c5367d68a34c6693dee9660a4d696520e6aec0)), closes [#82](https://github.com/Safe-DS/Stub-Generator/issues/82)
* Fixed a bug where results in stubs would not be named ([#131](https://github.com/Safe-DS/Stub-Generator/issues/131)) ([4408c84](https://github.com/Safe-DS/Stub-Generator/commit/4408c84da58dd84e1843d4fa39d04c1880088917)), closes [#100](https://github.com/Safe-DS/Stub-Generator/issues/100)
* Fixed a bug which prevented mypy version update ([#107](https://github.com/Safe-DS/Stub-Generator/issues/107)) ([501d2cd](https://github.com/Safe-DS/Stub-Generator/commit/501d2cdb836de1fa46fd5a25619c44d5143053d2))
* Fixed the stubs generator ([#108](https://github.com/Safe-DS/Stub-Generator/issues/108)) ([9ad6df6](https://github.com/Safe-DS/Stub-Generator/commit/9ad6df6143b3149dd8699593dcb6761d755d8181)), closes [#80](https://github.com/Safe-DS/Stub-Generator/issues/80)
* Generated names of callback results start with result, not with param ([#104](https://github.com/Safe-DS/Stub-Generator/issues/104)) ([6e696e9](https://github.com/Safe-DS/Stub-Generator/commit/6e696e9f4ff57ca241706406d937275dec22cc4d)), closes [#85](https://github.com/Safe-DS/Stub-Generator/issues/85)
* Include lines of examples that start with `...` ([#130](https://github.com/Safe-DS/Stub-Generator/issues/130)) ([3477b4a](https://github.com/Safe-DS/Stub-Generator/commit/3477b4adf702da7f99bd90e45d6c3561ef287f0e)), closes [#129](https://github.com/Safe-DS/Stub-Generator/issues/129)
* No "// TODO ..." if return type is explicitly `None` ([#111](https://github.com/Safe-DS/Stub-Generator/issues/111)) ([08e345f](https://github.com/Safe-DS/Stub-Generator/commit/08e345fcb5e1bc1227691cd70df8d994242bfe69)), closes [#83](https://github.com/Safe-DS/Stub-Generator/issues/83)
* Removed the Epydoc parser ([#89](https://github.com/Safe-DS/Stub-Generator/issues/89)) ([684a101](https://github.com/Safe-DS/Stub-Generator/commit/684a101ca5369bc2aff0e8c76804b0c3e533f60a))
* Replaced tabs with 4 spaces ([#105](https://github.com/Safe-DS/Stub-Generator/issues/105)) ([8e7aa5d](https://github.com/Safe-DS/Stub-Generator/commit/8e7aa5df1c4f5c81e63fe7cb00927c8853f17d8f)), closes [#84](https://github.com/Safe-DS/Stub-Generator/issues/84)
* The file structure of stubs resembles the "package" path. ([#106](https://github.com/Safe-DS/Stub-Generator/issues/106)) ([ff1800e](https://github.com/Safe-DS/Stub-Generator/commit/ff1800e23fbb3631e6fe8fa94de59e19910e4a04)), closes [#81](https://github.com/Safe-DS/Stub-Generator/issues/81)
* Translation of callable ([#102](https://github.com/Safe-DS/Stub-Generator/issues/102)) ([c581e6a](https://github.com/Safe-DS/Stub-Generator/commit/c581e6a66324965afc627985b79f77351fa57ff7)), closes [#88](https://github.com/Safe-DS/Stub-Generator/issues/88) [#88](https://github.com/Safe-DS/Stub-Generator/issues/88)

## [0.2.0](https://github.com/Safe-DS/Stub-Generator/compare/v0.1.0...v0.2.0) (2024-03-29)


### Features

* Added generation for Safe-DS stubs files ([#33](https://github.com/Safe-DS/Stub-Generator/issues/33)) ([ab45b45](https://github.com/Safe-DS/Stub-Generator/commit/ab45b459b99ba8db0b41bb34d94dbffec7387a28))
* Correct stubs for TypeVars ([#67](https://github.com/Safe-DS/Stub-Generator/issues/67)) ([df8c5c9](https://github.com/Safe-DS/Stub-Generator/commit/df8c5c9bb992717b3113b17d6c76e630cb74538b)), closes [#63](https://github.com/Safe-DS/Stub-Generator/issues/63)
* Create stubs for public methods of inherited internal classes ([#69](https://github.com/Safe-DS/Stub-Generator/issues/69)) ([71b38d7](https://github.com/Safe-DS/Stub-Generator/commit/71b38d7635b59ef6892c17624472a32db464a940)), closes [#64](https://github.com/Safe-DS/Stub-Generator/issues/64)
* Rework import generation for stubs. ([#50](https://github.com/Safe-DS/Stub-Generator/issues/50)) ([216e179](https://github.com/Safe-DS/Stub-Generator/commit/216e1790cecced0d6a76313cb2ed2f725baf684f)), closes [#38](https://github.com/Safe-DS/Stub-Generator/issues/38) [#24](https://github.com/Safe-DS/Stub-Generator/issues/24) [#38](https://github.com/Safe-DS/Stub-Generator/issues/38) [#24](https://github.com/Safe-DS/Stub-Generator/issues/24)
* Safe-DS stubs also contain docstring information. ([#78](https://github.com/Safe-DS/Stub-Generator/issues/78)) ([bdb43bd](https://github.com/Safe-DS/Stub-Generator/commit/bdb43bdd5e190251c85be67b74c38e8f57785c24))
* Stubs are created for referenced declarations in other packages ([#70](https://github.com/Safe-DS/Stub-Generator/issues/70)) ([522f38d](https://github.com/Safe-DS/Stub-Generator/commit/522f38d64ea812b8eca52ae4f8ac2426e74fbf01)), closes [#66](https://github.com/Safe-DS/Stub-Generator/issues/66)


### Bug Fixes

* Some packages couldn't be analyzed ([#51](https://github.com/Safe-DS/Stub-Generator/issues/51)) ([fa3d020](https://github.com/Safe-DS/Stub-Generator/commit/fa3d020a5b742c5d1e46bc17dc66eff794cced19)), closes [#48](https://github.com/Safe-DS/Stub-Generator/issues/48)
* Stub generation testing and fixing of miscellaneous bugs ([#76](https://github.com/Safe-DS/Stub-Generator/issues/76)) ([97b0ab3](https://github.com/Safe-DS/Stub-Generator/commit/97b0ab3eb6e3bfd69edd8802af3370ccd4dfca07))

## [0.1.0](https://github.com/Safe-DS/Stub-Generator/compare/v0.0.1...v0.1.0) (2023-11-29)


### Features

* drop Python 3.10 and add Python 3.12 ([#23](https://github.com/Safe-DS/Stub-Generator/issues/23)) ([091826d](https://github.com/Safe-DS/Stub-Generator/commit/091826d39eae4b962028d505989376a407901dd1))
* port code from `library-analyzer` ([#16](https://github.com/Safe-DS/Stub-Generator/issues/16)) ([5e0b3b1](https://github.com/Safe-DS/Stub-Generator/commit/5e0b3b1d11172baeb70fbfd49066580d8fe4152d))


### Bug Fixes

* Added handling for boolean default values for parameters ([#25](https://github.com/Safe-DS/Stub-Generator/issues/25)) ([1ff250d](https://github.com/Safe-DS/Stub-Generator/commit/1ff250d1612bf26b2b7c043bc36d588d5992ecff))
* **deps-dev:** bump urllib3 from 2.0.6 to 2.0.7 ([#26](https://github.com/Safe-DS/Stub-Generator/issues/26)) ([ff1a33b](https://github.com/Safe-DS/Stub-Generator/commit/ff1a33bfef409c5ae651fc8c89b56b3b70bb0748))
* Fixed bugs for analyzing packages and api data creation. ([#27](https://github.com/Safe-DS/Stub-Generator/issues/27)) ([80215a3](https://github.com/Safe-DS/Stub-Generator/commit/80215a334c2d5bba566e2592fb05568f4a2d3048))
