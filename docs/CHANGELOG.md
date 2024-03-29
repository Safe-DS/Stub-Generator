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
