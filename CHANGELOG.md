# CHANGELOG



## v0.22.7 (2023-12-05)

### Documentation

* docs: add instructions to install from environment.yml ([`23a703a`](https://github.com/Sieboldianus/TagMaps/commit/23a703aa81549aae0e901a59654a6fed2d728459))

* docs: add mapnik rendering link ([`b931cad`](https://github.com/Sieboldianus/TagMaps/commit/b931cad1285a4c6922ee0848ec3f49a89fa3d9cf))

* docs: add note to environment.yml for Windows pinning ([`4403e0c`](https://github.com/Sieboldianus/TagMaps/commit/4403e0cf4a058d26ddf642c3dba0e248bf5fc667))

### Fix

* fix: do not abort in case of unknown emoji unicode character ([`a69fd5f`](https://github.com/Sieboldianus/TagMaps/commit/a69fd5f90a6074ab726d4d2946004f5165a489b0))

* fix: emoji column not correctly parsed ([`362ad8f`](https://github.com/Sieboldianus/TagMaps/commit/362ad8fdee3e10c6a11b208dd99ef287bb0983ef))


## v0.22.6 (2023-08-04)

### Build

* build: Fix python-semantic-release version_variabl[2], add upstream issue ([`5d9a1d6`](https://github.com/Sieboldianus/TagMaps/commit/5d9a1d67c9056350dd840529564dad2ff4f4a713))

### Fix

* fix: Semantic-release flow for &gt;8.x.x ([`ae7c077`](https://github.com/Sieboldianus/TagMaps/commit/ae7c0775e02c9a7fab3713955cba937588a623d9))

### Unknown

* Manual version bump ([`9f42151`](https://github.com/Sieboldianus/TagMaps/commit/9f42151001c96cc55b58d784e3c5091303d4099c))


## v0.22.5 (2023-08-04)

### Build

* build: Fix make_release.sh correct order of params ([`3f70be0`](https://github.com/Sieboldianus/TagMaps/commit/3f70be0183a1734d762d80240876536a7a8fe4d6))

* build: Add build and release script for semantic-release &gt;=8.0.0 ([`d871acb`](https://github.com/Sieboldianus/TagMaps/commit/d871acb1c4cd1694f18b0570d9df50c30582b6af))

* build: Pin emoji package upper version to &lt;3.0.0 ([`8b22b60`](https://github.com/Sieboldianus/TagMaps/commit/8b22b60231e4d3c495a571a59b34700ff77b1a53))

### Ci

* ci: Bump to image version 0.4.0 ([`a2c4f98`](https://github.com/Sieboldianus/TagMaps/commit/a2c4f982e98c9d914fe78a11453ddca08de6dd66))

### Documentation

* docs: Add information to angular commit message convention system ([`124f012`](https://github.com/Sieboldianus/TagMaps/commit/124f012b45b816e77c83e6d03d08bf29e53dbe5f))

* docs: Add gcc to pre-dependencies on linux ([`00d4710`](https://github.com/Sieboldianus/TagMaps/commit/00d4710320746053f2496524abd97941701f5153))

### Fix

* fix: demojize not found in emoji package ([`4b4afda`](https://github.com/Sieboldianus/TagMaps/commit/4b4afda15b1c247d4cdfa03537d4d5107ac08839))

* fix: Emoji are only parsed from post_body, not from emoji column ([`5a0cc47`](https://github.com/Sieboldianus/TagMaps/commit/5a0cc470fb69653f18715a428cbff08c2511a914))

* fix: Python in requirements.txt not allowed ([`b284554`](https://github.com/Sieboldianus/TagMaps/commit/b284554d9af73fd44a95b420288a31bc58409ba0))

### Style

* style: Code style formatting in utils.py follow Black ([`c4b732e`](https://github.com/Sieboldianus/TagMaps/commit/c4b732ed22f469c16a5e9264b7fd6a65ac08065c))

* style: Code formatting in load_data.py ([`e5f3bda`](https://github.com/Sieboldianus/TagMaps/commit/e5f3bda7d383a0c0cd24a09a184ca857b730c76d))

### Unknown

* Fix code typo ([`c6b1536`](https://github.com/Sieboldianus/TagMaps/commit/c6b1536314dcad196a040d76b55a8fa37add1a24))


## v0.22.4 (2023-07-21)

### Ci

* ci: Pin CI container, use installation with pip instead of conda ([`757ca7e`](https://github.com/Sieboldianus/TagMaps/commit/757ca7e8ece1138f4065217f3be3a17fb9ddfdc1))

### Documentation

* docs: Add instructions to install on Linux and from requirements.txt ([`07cc618`](https://github.com/Sieboldianus/TagMaps/commit/07cc618175f6cfa9b0da1abf26d9932af752283e))

* docs: Add instructions to use conda together with no-dependencies and --editable flags ([`d8143db`](https://github.com/Sieboldianus/TagMaps/commit/d8143db52c19b5867c7e981618b847076a1f9190))

### Fix

* fix: requirements.txt containing misspelled and missing dependencies ([`54fa4c1`](https://github.com/Sieboldianus/TagMaps/commit/54fa4c122c75ea580bbe136864815dd1ee265dc5))

* fix: HDBSCAN TypeError: &#39;numpy.float64&#39;, [1]

[1]: https://github.com/scikit-learn-contrib/hdbscan/issues/600 ([`4f9a652`](https://github.com/Sieboldianus/TagMaps/commit/4f9a652111d1fa28e393051df64e8a7e9f179cca))

* fix: tri.vertices - Delaunay object has no attribute vertices

See [1]

[1]: https://stackoverflow.com/a/62664667/4556479 ([`133cfdc`](https://github.com/Sieboldianus/TagMaps/commit/133cfdccbb2f78ae21c5fcb09f08ed9ee90d46f9))

### Unknown

* Fix HDBSCAN TypeError: &#39;numpy.float64&#39;, [1]

[1]: https://github.com/scikit-learn-contrib/hdbscan/issues/600 ([`422b27a`](https://github.com/Sieboldianus/TagMaps/commit/422b27a23cf7bf98b0e3c7136500307043cad074))

* Minor readme typo ([`bddb0cd`](https://github.com/Sieboldianus/TagMaps/commit/bddb0cdbaeabf6d1aef6acf23ea945f9deb34bea))


## v0.22.2 (2023-05-16)

### Documentation

* docs: Restructure Developers section ([`ae93e68`](https://github.com/Sieboldianus/TagMaps/commit/ae93e686040d23e75117fcd1053ede7502da4bdb))

* docs: Add high-level update to changelog ([`6a1bc1f`](https://github.com/Sieboldianus/TagMaps/commit/6a1bc1f9db9355ff6ba1efd99cac9a1b510945d1))

### Unknown

* deps: Remove obsolete explicit dependencies ([`f773239`](https://github.com/Sieboldianus/TagMaps/commit/f773239beed715314d1076d6e9d24da22bc6c7b0))

* Fix typo ([`ce7fb84`](https://github.com/Sieboldianus/TagMaps/commit/ce7fb84a7c913513af692be532af808c7b57bb7e))

* Update README.md ([`7c57bf3`](https://github.com/Sieboldianus/TagMaps/commit/7c57bf3fbea6d20ac46ba19607002ac1208d9f47))

* dep: Pin fiona only in conda-build ([`e4f08fe`](https://github.com/Sieboldianus/TagMaps/commit/e4f08fe94cbdbedf42819700806c8884aaf9f796))

* Fix src links in readme ([`5cf5b74`](https://github.com/Sieboldianus/TagMaps/commit/5cf5b742ad304b1ee54fe3e545f24cc6d574a787))

* Fix pipeline.svg badge in Readme.md ([`9b26dd6`](https://github.com/Sieboldianus/TagMaps/commit/9b26dd60571c3e2fe53eb1527f5aa04d18241853))


## v0.22.0 (2023-05-10)

### Ci

* ci: Fix oudated path ([`889d678`](https://github.com/Sieboldianus/TagMaps/commit/889d678cf81ef28af52bf8fa118df64d34f72690))

### Documentation

* docs: Add basic description of project structure and release-flow for developers to documentation ([`f7e77db`](https://github.com/Sieboldianus/TagMaps/commit/f7e77db0754a70d4e92dafdd3ec9f19c4024a394))

* docs: Add purpose as docstring to environment.yml ([`5583627`](https://github.com/Sieboldianus/TagMaps/commit/558362784de10c360d88ed0be10ca5939c29bc38))

### Feature

* feat: Migrate project to pyproject.toml only ([`fc79efd`](https://github.com/Sieboldianus/TagMaps/commit/fc79efd653c982dc0db20e8a7f64110c152c037d))

### Refactor

* refactor: Migrate to src-layout ([`cde7b28`](https://github.com/Sieboldianus/TagMaps/commit/cde7b2817d6af7a25cbf36719971350615ab13e5))

### Unknown

* Clarify manual release flow ([`6fa1d4a`](https://github.com/Sieboldianus/TagMaps/commit/6fa1d4a4e9208c7870b7e0fdf21ec99ef0724d17))

* Fix typo ([`2c9de49`](https://github.com/Sieboldianus/TagMaps/commit/2c9de491f825b472f4b2afe5ff18a557988c0e34))


## v0.21.2 (2023-05-10)

### Documentation

* docs: Fix link in README.md ([`2429c9b`](https://github.com/Sieboldianus/TagMaps/commit/2429c9bd98a80d91a6c89eb337436d61f880b439))

* docs: Update table of contents ([`dba0e2e`](https://github.com/Sieboldianus/TagMaps/commit/dba0e2e1ad7101626b2a2c1491e9e8897d191096))

* docs: Add CHANGELOG to documentation ([`adfe3e5`](https://github.com/Sieboldianus/TagMaps/commit/adfe3e569d8119f5ae72bc5fcc855fcaa2c4cf8c))

### Fix

* fix: GDAL/Fiona ImportError: DLL load failed while importing _env (Windows)

fixes: #3

reported: https://github.com/conda-forge/fiona-feedstock/issues/213

Remove pinning of fiona 1.8.22 when upstream resolved ([`7952df3`](https://github.com/Sieboldianus/TagMaps/commit/7952df3d5693cf99a2c6d65967a7951a436b36b9))

### Style

* style: Code formatting update ([`d1322f5`](https://github.com/Sieboldianus/TagMaps/commit/d1322f5f435d764fb134c0fd37a79790d44cc475))

* style: Refactor code style formatting ([`71b644e`](https://github.com/Sieboldianus/TagMaps/commit/71b644e3952de851e03cd779ff3880fdab431d35))

### Unknown

* dep: Remove descartes from dependencies, incorporate PolygonPatch natively ([`171880c`](https://github.com/Sieboldianus/TagMaps/commit/171880c0ae41c2a2eebea9c357776b735ac4fc38))

* Fix typo ([`427e956`](https://github.com/Sieboldianus/TagMaps/commit/427e956bd4c8de611342819b54f179052414b51d))

* Add CHANGELOG history ([`7c38d9e`](https://github.com/Sieboldianus/TagMaps/commit/7c38d9ec2e8c0646c1db78a8322e79fe757c1664))


## v0.21.1 (2022-11-25)

### Chore

* chore: Update dependency pinnings ([`4488817`](https://github.com/Sieboldianus/TagMaps/commit/4488817743b2e0fee48fa9f99a9380f47be7e9d2))

### Documentation

* docs: Add comparison graphic for Mapnik/ArcPro rendering ([`e15682d`](https://github.com/Sieboldianus/TagMaps/commit/e15682d2626d883f9997b9121705789da91fcb1c))

### Fix

* fix: Matplotlib fig.canvas.set_window_title() deprecated in Matplotlib&gt;=3.4 ([`6459d5f`](https://github.com/Sieboldianus/TagMaps/commit/6459d5f8ee4395677fa3d1eedf6d8dda8fd40eda))

* fix: EMOJI_UNICODE deprecated in emoji&gt;=2.0.0 ([`9d1e243`](https://github.com/Sieboldianus/TagMaps/commit/9d1e2438ce81cbf8e65f3d47fad3c17afbcfbd61))

### Unknown

* Update README.md ([`0e2c341`](https://github.com/Sieboldianus/TagMaps/commit/0e2c34100094a610725996bac66fd94f5f0010a6))

* Update TOC ([`66637a5`](https://github.com/Sieboldianus/TagMaps/commit/66637a54fb87f1189c26c90d7b6d1f3509b0c140))

* Update Readme ([`bb4cd76`](https://github.com/Sieboldianus/TagMaps/commit/bb4cd760fb516c22f02978312499790eb75e098e))

* Update Readme ([`5016aeb`](https://github.com/Sieboldianus/TagMaps/commit/5016aeb6d30700747dce6d4def8dd4f7990adafb))

* Update Readme ([`f57b85f`](https://github.com/Sieboldianus/TagMaps/commit/f57b85f4f0bca135f286781bd7d4e855ffe03526))

* Fix missing file in docs ([`a0e08fa`](https://github.com/Sieboldianus/TagMaps/commit/a0e08fa1f2ffaefe86e7e30194b6491ab7d82913))


## v0.21.0 (2022-07-27)

### Chore

* chore: Remove obsolete files ([`b48556f`](https://github.com/Sieboldianus/TagMaps/commit/b48556f13623be1f51666f4a714b564cf9ca4784))

### Ci

* ci: Change gitlab runner ([`4114f07`](https://github.com/Sieboldianus/TagMaps/commit/4114f076b4ff9d38fc7a918bad7d75f83017d1dd))

* ci: Change gitlab runner ([`6506f5c`](https://github.com/Sieboldianus/TagMaps/commit/6506f5ca5f233c3555bf2129ad4aef53b8ddbdc9))

### Documentation

* docs: Add section on visualization with Mapnik ([`25dbb2c`](https://github.com/Sieboldianus/TagMaps/commit/25dbb2c0208f42d844fe92d6c863f909ce395f4f))

* docs: Add webm link to animation ([`f1190c8`](https://github.com/Sieboldianus/TagMaps/commit/f1190c8521851d93a13d3227ec031b51928c59fe))

* docs: Add label placement animation ([`82c987d`](https://github.com/Sieboldianus/TagMaps/commit/82c987d3af76b9c7343d5088adc8c1ae587e3b6d))

* docs: Remove deprecated cx_freeze references ([`92098e6`](https://github.com/Sieboldianus/TagMaps/commit/92098e6bd7d2817ca2c537401d3a19b9dc1dacbf))

* docs: Add publication link ([`9e3cb16`](https://github.com/Sieboldianus/TagMaps/commit/9e3cb163123ebbc87207d9ad56a6e457ac3fd28a))

* docs: Improve readme for resource folder ([`f8ef9f7`](https://github.com/Sieboldianus/TagMaps/commit/f8ef9f746d5cb0bfe14022c182f3c06e8fbb1040))

* docs: Add note to resources folder ([`ff9fe96`](https://github.com/Sieboldianus/TagMaps/commit/ff9fe962acbb2c833551e218137cab683e04fbcd))

### Feature

* feat: Add export to Mapnik ([`9db0d0d`](https://github.com/Sieboldianus/TagMaps/commit/9db0d0dc0a266f9eef7c3aac5bf663337c096f80))

### Refactor

* refactor: Rename file ([`117119d`](https://github.com/Sieboldianus/TagMaps/commit/117119db3401a3bfaaa4e988c9a897822357ec90))

### Style

* style: Remove spellcheck from ArcPro template; add legend ([`15b3db8`](https://github.com/Sieboldianus/TagMaps/commit/15b3db8bdf5702122fd24539458d11b3c8542931))

### Unknown

* This PR adds export to mapnik feature (enable with `--mapnik_export flag)`. See a Jupyter Notebook that illustrates how to visualize tag map output with mapnik [here](https://ad.vgiscience.org/tagmaps-mapnik-jupyter/01_mapnik-tagmaps.html). ([`81e0556`](https://github.com/Sieboldianus/TagMaps/commit/81e05562a492e477e6248b30b5253c92bc46bf13))

* Fix gif not showing in Github due to Camo CDN ([`aa94dfe`](https://github.com/Sieboldianus/TagMaps/commit/aa94dfe4294aa1ba5c6f773b488e4d54cb385a8c))

* Fix typo ([`21d1215`](https://github.com/Sieboldianus/TagMaps/commit/21d1215e7d20ec1c2a30bb0fdd0d9633d5cc4a54))

* Fix DOI link ([`583ea7c`](https://github.com/Sieboldianus/TagMaps/commit/583ea7c0be6c4f18c0744dc95092ed23ce6061cd))

* resources: Add ArcPro 2.8.0 template ([`8b8b66f`](https://github.com/Sieboldianus/TagMaps/commit/8b8b66f372481cd51eda142b8f7b37b2d418dc08))

* resources: Add layer symbology file for hot spot analysis ([`fb158db`](https://github.com/Sieboldianus/TagMaps/commit/fb158db1b0142557bb5727795be11779c259b6ef))

* resources: Add Layout file for ArcPro 2.9.0 ([`43dcc12`](https://github.com/Sieboldianus/TagMaps/commit/43dcc12f2fdffcf60df5a8181d5357e85de755f3))


## v0.20.12 (2022-01-19)

### Chore

* chore: Add readme to setup.cfg ([`f9f59c2`](https://github.com/Sieboldianus/TagMaps/commit/f9f59c26f5d539b5146c1037eb16f1da4bbf8957))

### Fix

* fix: ShapelyDeprecationWarning use geoms property ([`1352ea9`](https://github.com/Sieboldianus/TagMaps/commit/1352ea94feb77db37b5305a9f6281e5c5b2834b5))


## v0.20.11 (2022-01-18)

### Chore

* chore: Add cx-freeze shortcut to test run ([`fa5c751`](https://github.com/Sieboldianus/TagMaps/commit/fa5c751c79e2c2a3a2e1a41f01393d197ba8f3e8))

* chore: Move template ([`6ee8032`](https://github.com/Sieboldianus/TagMaps/commit/6ee8032b866d853e26962cdf1fb57b58a896a1ad))

* chore: fix yml formatting for pinning versions ([`508f7e1`](https://github.com/Sieboldianus/TagMaps/commit/508f7e1663f95b822619ba613c7dd12242144a7c))

* chore: Fix cx-freeze build process ([`aa6595e`](https://github.com/Sieboldianus/TagMaps/commit/aa6595e84b649e0a28c14cf7fc6f333db447af42))

### Documentation

* docs: Add git revision date to pages ([`728dcd4`](https://github.com/Sieboldianus/TagMaps/commit/728dcd4fcaa17622259901b1477a8ff505889e30))

* docs: Improve formatting and revise structure ([`c1d1cc0`](https://github.com/Sieboldianus/TagMaps/commit/c1d1cc04a97dbe49ad2cd85f12efc71db778ca89))

* docs: cleanup changelog ([`9ce4021`](https://github.com/Sieboldianus/TagMaps/commit/9ce40210cfe42620f1d99aaad687e37984c34f19))

### Fix

* fix: Deprecated shapely cascaded_union() ([`2dfb2a1`](https://github.com/Sieboldianus/TagMaps/commit/2dfb2a13ddc544b7cf78fffc9b7f47d4788b9678))


## v0.20.10 (2021-02-18)

### Chore

* chore: update dependency pinning for emoji and joblib ([`97491e3`](https://github.com/Sieboldianus/TagMaps/commit/97491e32b6e7cfcbca612ac6d02dbd46a5a2d728))

* chore: Use sed to get version string ([`326799e`](https://github.com/Sieboldianus/TagMaps/commit/326799e9fccc6e95ef013dc66416aa96238bb3e2))

### Ci

* ci: fix badge duplicate ([`f3d5a63`](https://github.com/Sieboldianus/TagMaps/commit/f3d5a63b60a1d38908ceb998597b12c1d07eade5))

### Documentation

* docs: correct order of pip --editable --no-deps ([`5c58cdd`](https://github.com/Sieboldianus/TagMaps/commit/5c58cdda327191796a0e37f9388ca0605b6dac75))

### Fix

* fix: Graphemes not found in newest emoji.UNICODE_EMOJI (emoji &gt;= v.1.0.1) ([`9952cd2`](https://github.com/Sieboldianus/TagMaps/commit/9952cd253d3637d8dff1304541720e9f37ea1abd))

### Refactor

* refactor: use absolute imports ([`b9dc11f`](https://github.com/Sieboldianus/TagMaps/commit/b9dc11f4ce759566ff4eed8acdcdd323d721aa74))

### Unknown

* resources: Add ArcPro Layout Template ([`df1caa6`](https://github.com/Sieboldianus/TagMaps/commit/df1caa63ec693d1cd116f1f691d0de3d66e17d43))

* Remove executable bit ([`b0393f6`](https://github.com/Sieboldianus/TagMaps/commit/b0393f6d52fedba95ca38443b2edfb28e7271206))


## v0.20.9 (2021-01-03)

### Chore

* chore: temporary pin joblib to 0.17.0, see [hdbscan](https://github.com/scikit-learn-contrib/hdbscan/issues/436) ([`b7b5401`](https://github.com/Sieboldianus/TagMaps/commit/b7b5401d5e25d72a13143d3af5289c4196f56193))

### Ci

* ci: remove pip search endpoint ([`28dd077`](https://github.com/Sieboldianus/TagMaps/commit/28dd077c09b1facf5c8e7d38b672bd7943302d5b))

### Fix

* fix: correct pin joblib ([`7c87979`](https://github.com/Sieboldianus/TagMaps/commit/7c879795975f7c3e54ce9088418f7dfc12b9e5c4))


## v0.20.8 (2021-01-03)


## v0.20.7 (2021-01-03)

### Unknown

* Merge branch &#39;dev&#39; ([`81315a2`](https://github.com/Sieboldianus/TagMaps/commit/81315a27bb4094abc2959b15c5cbf9ec23b7a472))


## v0.20.6 (2021-01-03)

### Documentation

* docs: add pip --editable note ([`c51d75a`](https://github.com/Sieboldianus/TagMaps/commit/c51d75aaa55e341e6a074fe01977a0504364da53))

### Fix

* fix: name not found on manual get_cluster_shapes_map() ([`6bd9d66`](https://github.com/Sieboldianus/TagMaps/commit/6bd9d665eabfce7ed6bb3dfe7f7549df61ee9dfb))

### Refactor

* refactor: remove whitespace ([`baf3307`](https://github.com/Sieboldianus/TagMaps/commit/baf33074f9c915bfdd8846e7382d042210d51c4e))


## v0.20.5 (2021-01-03)

### Chore

* chore: remove explicit dependencies joblib and six ([`f3e59a9`](https://github.com/Sieboldianus/TagMaps/commit/f3e59a9a50beba47db75242f9ef37bf3619fe385))

* chore: update MANIFEST.in (config) ([`57ca63e`](https://github.com/Sieboldianus/TagMaps/commit/57ca63ee28437793237e61134172f872aa3e5380))

* chore: update cx_freeze EPSH_SHARE env ([`d940f93`](https://github.com/Sieboldianus/TagMaps/commit/d940f93ddba63dd814ad0846f2956551e4eed638))

### Ci

* ci: Enable highlightjs in mkdocs ([`d3b63b1`](https://github.com/Sieboldianus/TagMaps/commit/d3b63b15821b0016eb99d09e4422cc6aa7126025))

* ci: add explicit channel ref for pylint and bitarray ([`c85773d`](https://github.com/Sieboldianus/TagMaps/commit/c85773dd27d91b6fb0622c042bf678fc5f94d6c3))

* ci: fix pylint f-strings formatting ([`0b4c311`](https://github.com/Sieboldianus/TagMaps/commit/0b4c31180e117c6b9d8b7bc68ef2142d1339609c))

### Documentation

* docs: minor rephrase of introduction ([`6f6ddfc`](https://github.com/Sieboldianus/TagMaps/commit/6f6ddfc45c6174a90ef90abaf8c902119cb1921a))

* docs: add super-submodule docstrings ([`2e98868`](https://github.com/Sieboldianus/TagMaps/commit/2e98868dd1a85fa2aafffdf9bd906a8aff8cc8da))

* docs: Update about section ([`d5c7878`](https://github.com/Sieboldianus/TagMaps/commit/d5c7878b47dc651f891e960a9758dd5e9a9ac59a))

* docs: update Linux install instructions ([`cf023dc`](https://github.com/Sieboldianus/TagMaps/commit/cf023dc0772cfb22630f38668ddce90be7d254cc))

* docs: enable API docs for __main__ ([`518b205`](https://github.com/Sieboldianus/TagMaps/commit/518b20551a29cdfb17f6e0ee7f8475866eb02800))

* docs: fix readme download link ([`1ff63ae`](https://github.com/Sieboldianus/TagMaps/commit/1ff63ae546f552cae5c559a76cb4adbf3f833dc4))

* docs: update release notes, add link to win-37 build

Merge cx_freeze bugfix branch ([`f224de2`](https://github.com/Sieboldianus/TagMaps/commit/f224de20d0d3e68a67c4d48443432ddf31893f5a))

* docs: update release notes, add link to win-37 build ([`5bfcc76`](https://github.com/Sieboldianus/TagMaps/commit/5bfcc76dafd9786fc7b7b66cc06a7313db3269f2))

### Fix

* fix: emoji flags split from grapheme clusters ([`c0512e3`](https://github.com/Sieboldianus/TagMaps/commit/c0512e33a11af0d4ef026b12453bff65954f1f85))

* fix: move from ThreadPool to threading.Thread/Queue, related to joblib freeze issue 1002 (see below)

See joblib issue [1002](https://github.com/joblib/joblib/issues/1002). For the frozen executable to function, additional modifications to hdbscan dependency are necessary, see [fork](https://github.com/Sieboldianus/hdbscan). ([`23995e2`](https://github.com/Sieboldianus/TagMaps/commit/23995e27d9d5b2382fb184cdeb074d7f80bf284f))

### Refactor

* refactor: remove remnants of pyproj &lt; 2.0.0 compatibility ([`7fb40e0`](https://github.com/Sieboldianus/TagMaps/commit/7fb40e0676346c7174960de4b4f5f2913bf17ae2))

### Unknown

* Enable titles_only for mkdocs ([`1c05a1b`](https://github.com/Sieboldianus/TagMaps/commit/1c05a1b0b108696a49af9462ecd0afca002fd042))

* pdoc3 exclude format update ([`1158d68`](https://github.com/Sieboldianus/TagMaps/commit/1158d68c0b5f5c75c4d0efe8a9452c2d7104b7f6))

* Fix minor typo ([`790426f`](https://github.com/Sieboldianus/TagMaps/commit/790426f7436baff5710ffe794268e150b436040e))

* Merge branch &#39;master&#39; of github.com:Sieboldianus/TagMaps ([`2639b6d`](https://github.com/Sieboldianus/TagMaps/commit/2639b6dc6dd6d90353eb317652c01b479e0c11b6))

* Merge branch &#39;joblib-threading-queue-example&#39; into dev ([`1a8f85f`](https://github.com/Sieboldianus/TagMaps/commit/1a8f85fe50e4f7ef47a6ae29470a9f078164bfab))


## v0.20.4 (2020-01-24)

### Chore

* chore: fix argdown repo link ([`ded9b35`](https://github.com/Sieboldianus/TagMaps/commit/ded9b35ac41e2192123b467501b41115b0df8d5f))

### Fix

* fix: wrong axis order of projected geometries

Long story: from pypro&lt;=1.9.6 to pyproj&gt;=2.0.0, methods of defining projections changed. The depreciated way allowed traditional order of lng-lat, the new projection-defeinition was using lat-lng by default, which caused final geometries to appear flipped. See [1](https://github.com/pyproj4/pyproj/issues/355#issuecomment-507896053) and [2](https://gis.stackexchange.com/a/326919/33092) ([`0893769`](https://github.com/Sieboldianus/TagMaps/commit/08937694f4e5f1b28421cb755b4ac584223a458f))


## v0.20.3 (2020-01-21)

### Chore

* chore: fix cx_freeze setup, update instructions ([`9876fc6`](https://github.com/Sieboldianus/TagMaps/commit/9876fc655cea2245de9481c024d280bddde5adde))

### Documentation

* docs: add build release for v0.20.2 (win-amd64) ([`8e22e6b`](https://github.com/Sieboldianus/TagMaps/commit/8e22e6b9a1aa7832d6023ab141b2f068172c25db))

* docs(readme): fix conda badge ([`541240e`](https://github.com/Sieboldianus/TagMaps/commit/541240e8409c291ebb97eb85772bee489c43a2ab))

* docs(readme): update changelog ([`c56a152`](https://github.com/Sieboldianus/TagMaps/commit/c56a152d18a17e33264b0100bdb5aac0e50156d9))

### Fix

* fix: use correct syntax of crs init for pyproj.Proj ([`fa19480`](https://github.com/Sieboldianus/TagMaps/commit/fa19480e630bba268ef2e165e4755473d401e1cc))

### Unknown

* Merge branch &#39;master&#39; of github.com:Sieboldianus/TagMaps ([`4ced2ec`](https://github.com/Sieboldianus/TagMaps/commit/4ced2ec4f7fbc82c8362ecd10790be3a10ec701c))

* Update argdown repo url ([`6ea1f9b`](https://github.com/Sieboldianus/TagMaps/commit/6ea1f9be1d1331f8af43882699a1f9b7af0fdd49))

* Depend on matplotlib-base in conda env ([`321030e`](https://github.com/Sieboldianus/TagMaps/commit/321030e58cc87736902716f73e2f7f270668cc84))

* Fixup docs ([`4b55e43`](https://github.com/Sieboldianus/TagMaps/commit/4b55e431272dfb54667461c3ae91686b176b9a89))

* Fix typo ([`6044aad`](https://github.com/Sieboldianus/TagMaps/commit/6044aad98ed523eb0ba30e387b4843193e9a65bd))


## v0.20.2 (2019-11-26)

### Chore

* chore: update ci registry images ([`04f22d4`](https://github.com/Sieboldianus/TagMaps/commit/04f22d43e981aad8c04231cf9d2b5091730c4e5b))

* chore: use explicit flags in cmd executables ([`7ee86f8`](https://github.com/Sieboldianus/TagMaps/commit/7ee86f863e7be6fbf92458ae25573be03096fe16))

### Documentation

* docs(readme): minor spelling ([`06b3645`](https://github.com/Sieboldianus/TagMaps/commit/06b3645c192869b84de53ae0d2f71f054af63169))

* docs(readme): instructions for cloning resources folder ([`dc4406d`](https://github.com/Sieboldianus/TagMaps/commit/dc4406d5c60a945d6ddb7bb0f2d8fc0f03aa963f))

* docs: change license to CC BY-SA 4.0 ([`42a3b24`](https://github.com/Sieboldianus/TagMaps/commit/42a3b24a93cc4bdab1ac29830a11d899e18b1d4a))

### Fix

* fix: fix type hints, migrate to dataclasses

Note: tagmaps requires python 3.7 from this commit on due to dataclass ([`fbc0dbe`](https://github.com/Sieboldianus/TagMaps/commit/fbc0dbee9f80df5ec2fa534903f9aa3a77966a9b))

* fix: use debug for unimportant parse issues ([`d33ebb1`](https://github.com/Sieboldianus/TagMaps/commit/d33ebb1073572f9abf15711c044c06eff57bb739))

* fix: variable undefined for --statistics_only ([`26ba512`](https://github.com/Sieboldianus/TagMaps/commit/26ba512cc08521b13588b8ad22ce0d126f21651d))

* fix: raise warning on missing key in file header ([`d70b2f1`](https://github.com/Sieboldianus/TagMaps/commit/d70b2f1caf3bbd416addd1fff3bf54f0edfdd4ec))

* fix: variable not defined for --statistics_only ([`f7d9acf`](https://github.com/Sieboldianus/TagMaps/commit/f7d9acf6c76be9d2dc17458d0cd93f934548eca7))

* fix: override of tagmaps logger in cli mode ([`5f2ff0c`](https://github.com/Sieboldianus/TagMaps/commit/5f2ff0c10fbe010785ae511a2dc9a983a1075af3))

* fix: catch invalid literals in post count ([`762a5fa`](https://github.com/Sieboldianus/TagMaps/commit/762a5fa9640bb71e8ca4205246706d008531b7bc))

### Refactor

* refactor: use set comprehension ([`8f65af6`](https://github.com/Sieboldianus/TagMaps/commit/8f65af61ea0567897c692ee5947ff43186a39a15))

* refactor: code formatting ([`a4c5f6d`](https://github.com/Sieboldianus/TagMaps/commit/a4c5f6d039d0558094028728a2bb2ff7b925f13a))

### Unknown

* Merge branch &#39;dev&#39; ([`f96f3d8`](https://github.com/Sieboldianus/TagMaps/commit/f96f3d861a564a82e4877a70bf78911f3d84daaf))

* Merge branch &#39;dev&#39; ([`a101a14`](https://github.com/Sieboldianus/TagMaps/commit/a101a14e6724a7dde3f7a740c7d886361fcc5cc7))

* Fix CI ([`6d2c05c`](https://github.com/Sieboldianus/TagMaps/commit/6d2c05c53051ae6fdac424fd5dc2bd411cc3bcc4))

* Remove ci_env packages from environment_ci.yml ([`047fe3c`](https://github.com/Sieboldianus/TagMaps/commit/047fe3cdfc372f2a115de3fcc5fb2ffa1f5d6c58))

* Merge branch &#39;dev&#39; of gitlab.vgiscience.de:ad/TagMaps into dev ([`faf8ff9`](https://github.com/Sieboldianus/TagMaps/commit/faf8ff9f7071f845f1329ab90efd0923cbea4fa0))

* Minor spelling ([`8558a02`](https://github.com/Sieboldianus/TagMaps/commit/8558a02e640c680a0f8973d7d4a0edc1cceac6ed))

* Minor spelling ([`d5ecb76`](https://github.com/Sieboldianus/TagMaps/commit/d5ecb766218c334ed4868e524a2b89b9120d05f9))

* Remove conda recipe from repo ([`263ae80`](https://github.com/Sieboldianus/TagMaps/commit/263ae80cc9ceaac61f9882e15bdefd5960877d25))

* Enable type annotations in pdoc ([`0119ef1`](https://github.com/Sieboldianus/TagMaps/commit/0119ef1feb1c072c0267937a3717c294dd242a9e))

* update instring stoplist ([`85f5b8f`](https://github.com/Sieboldianus/TagMaps/commit/85f5b8f55c8c62243fb7c30f5ae1274172880bf6))

* update global ignore list ([`04524b5`](https://github.com/Sieboldianus/TagMaps/commit/04524b5a26b790f89e5a4346702deec95188a7cd))

* output data errors only during debug ([`0b6617e`](https://github.com/Sieboldianus/TagMaps/commit/0b6617e5536468a47e8ab4460b5f942e71cba47e))

* fix list update ([`c583715`](https://github.com/Sieboldianus/TagMaps/commit/c58371529ab51ed78e1a1e6693311ed1988a0129))

* Minor update of docstrings ([`4fe5592`](https://github.com/Sieboldianus/TagMaps/commit/4fe55928beee52e95059115fbdfdb0e3cc7f2bd7))


## v0.20.1 (2019-10-08)

### Documentation

* docs: update cli flags info ([`f481823`](https://github.com/Sieboldianus/TagMaps/commit/f48182361dd42f84bd736d4c83daf2b9d74de8cf))

### Fix

* fix: do not ignore multiple input files in pipe ([`4325aea`](https://github.com/Sieboldianus/TagMaps/commit/4325aea6a10363613864cfadd638c6946f502add))

### Refactor

* refactor: remove duplicate report ([`b400e03`](https://github.com/Sieboldianus/TagMaps/commit/b400e031a11d4d7f6a4109c1631795158d8689fd))

### Style

* style: used fixed order for cluster types ([`4709a16`](https://github.com/Sieboldianus/TagMaps/commit/4709a16c3067e78449f8b98fa09a6bff1974c123))

### Unknown

* update stoplist ([`9a21163`](https://github.com/Sieboldianus/TagMaps/commit/9a21163f84b885a21af30bceb4b59c16d348657e))

* add missing arcmap document ressource emf ([`071d45f`](https://github.com/Sieboldianus/TagMaps/commit/071d45f143b89ec7b0941553fd1333e41bd24a44))


## v0.20.0 (2019-08-30)

### Chore

* chore: fix argparse imports for ci ([`98e5c92`](https://github.com/Sieboldianus/TagMaps/commit/98e5c929917f270a111d6e6c2ab49aa32aad2ae8))

* chore: fix ci integration test ([`8c914a9`](https://github.com/Sieboldianus/TagMaps/commit/8c914a9eaefd1ead4743dc8ee7ec27ac82cda4a6))

* chore: add pdoc template folder to ci ([`788c267`](https://github.com/Sieboldianus/TagMaps/commit/788c267749060a5e9503b43aaa3a198fc3aefae0))

* chore: install argdown directly from repo ([`8791a17`](https://github.com/Sieboldianus/TagMaps/commit/8791a1711d2659b53cd545ac98f3dabf0c7b4583))

* chore: add gitlab-ci test branch ([`3c766ee`](https://github.com/Sieboldianus/TagMaps/commit/3c766ee980b37767ed9c2feff6e60a5282770a94))

* chore: add argdown to markdown conversion ([`989c7d8`](https://github.com/Sieboldianus/TagMaps/commit/989c7d81e578a9119e782385bd05798bb3a0f2e9))

* chore: update default args ([`23ac7b1`](https://github.com/Sieboldianus/TagMaps/commit/23ac7b17796fdd25b7ed0c2bd8772d2c48767961))

* chore: add argparse to markdown scripts ([`c61a396`](https://github.com/Sieboldianus/TagMaps/commit/c61a396430ea46400a78227a4abd90cb125160be))

* chore: add argdown to markdown conversion ([`f54f87a`](https://github.com/Sieboldianus/TagMaps/commit/f54f87a75b840534157299cf40403e88c8171dad))

* chore: update default args ([`3b920d6`](https://github.com/Sieboldianus/TagMaps/commit/3b920d663de0c282373b2ae7deed920ffa5dd5bb))

* chore: fix conda docker version ([`827093d`](https://github.com/Sieboldianus/TagMaps/commit/827093db004d8de5a1362ddbfdd487b933302457))

* chore: output conda version in ci ([`fc4601d`](https://github.com/Sieboldianus/TagMaps/commit/fc4601dd477120e990d19d116de10969b4d2cc56))

### Documentation

* docs: format Note ([`22274ec`](https://github.com/Sieboldianus/TagMaps/commit/22274ecd7303a83d6714b5df2f484f8f8cb1f48f))

* docs: update order of suggested installation ways ([`60b98db`](https://github.com/Sieboldianus/TagMaps/commit/60b98dbddd6a39193c4c25d397de9b54f336e51b))

* docs: add custom logo to api refererence ([`7c4251b`](https://github.com/Sieboldianus/TagMaps/commit/7c4251b2543de8b204b973ca914bcef1bd7eff26))

* docs: update index ([`db4df26`](https://github.com/Sieboldianus/TagMaps/commit/db4df26084dcf89bc3f1bd5e1afd386b60f5ce73))

* docs: add cli Arguments and Usage ([`8258c9f`](https://github.com/Sieboldianus/TagMaps/commit/8258c9f678f4d89e0bce0fcee06e0117732edf71))

* docs: add cli Arguments and Usage ([`e648fba`](https://github.com/Sieboldianus/TagMaps/commit/e648fba815466a69eb54e1f3d79a9baf7d7b4e02))

* docs: rename theory to concept ([`0f86750`](https://github.com/Sieboldianus/TagMaps/commit/0f867505a8556c4164bbff2ca96a048d9c211e02))

### Feature

* feat: add cli options for additional selection and stoplists (emoji, tags, locations)

This commit includes:
- clean up of cli flags
- added help-info
- minor refactor of config.py ([`62ace7f`](https://github.com/Sieboldianus/TagMaps/commit/62ace7f934939c438b5e7be58b0c66756320b822))

### Fix

* fix: handle none-existing toplists ([`a488f0e`](https://github.com/Sieboldianus/TagMaps/commit/a488f0e4ca07b4d49e58a9ca7f08b16476a129c3))

### Refactor

* refactor: improve syntax formatting ([`b280d43`](https://github.com/Sieboldianus/TagMaps/commit/b280d4383802beeafcd84389c89fcbeb1ffb9b9c))

* refactor: revision of command line interface

This is not a pure refactor,
since it includes some additional cli flags:
* cluster_cut_distance
* stoplists (tags, places, user)
* shapefile_exclude

There&#39;re also some issues cleaned with Path converson, which is now handled in parse_args() ([`e9f98b4`](https://github.com/Sieboldianus/TagMaps/commit/e9f98b4cc2cf3e759f1953275594bb9c53efb391))

* refactor: separate method ([`663542f`](https://github.com/Sieboldianus/TagMaps/commit/663542f11b5ec2a080390efe4dbe5d8fbf80de56))

### Unknown

* fix minor typo ([`4d2f08b`](https://github.com/Sieboldianus/TagMaps/commit/4d2f08b30ae7e1125132656a4504493179f2fe58))

* update stoplist ([`377b2dd`](https://github.com/Sieboldianus/TagMaps/commit/377b2dd01023e62f28fd22fb8e1c4f2e5ca95825))

* minor revisions to concept docs ([`faaf3bd`](https://github.com/Sieboldianus/TagMaps/commit/faaf3bd53ad6c478d2be6ca3f8b073ca373acb41))

* fix missing indent ([`4787a89`](https://github.com/Sieboldianus/TagMaps/commit/4787a896ddc2aed61a31b0a35a4a04c102c3a9d3))

* Update quick-guide ([`d772472`](https://github.com/Sieboldianus/TagMaps/commit/d77247230a73812dee4641e1410528612f11c96d))

* fix formatting of note-blocks (admonition) ([`66f17c2`](https://github.com/Sieboldianus/TagMaps/commit/66f17c2dc69891814a3ce3c2fdbaec23b58856f7))

* fix links to code in readme ([`331f1cc`](https://github.com/Sieboldianus/TagMaps/commit/331f1cc18fb9ad775d35a2a428ffc10d56d45c77))

* fix links in api reference ([`21b17f8`](https://github.com/Sieboldianus/TagMaps/commit/21b17f8aa03ed009b338f9888806d2a0ea72acf1))

* minor readme spelling correction ([`232b00e`](https://github.com/Sieboldianus/TagMaps/commit/232b00e223f27ab6bf0c418dd39afbd8552dbe09))

* minor readme formatting fix ([`3a7d20d`](https://github.com/Sieboldianus/TagMaps/commit/3a7d20d5757610a7ba0387b9e26055094b10b313))

* update api docs links ([`16941fe`](https://github.com/Sieboldianus/TagMaps/commit/16941fe288b7f4a23705a375678004657bc44bcf))

* fix minor typo ([`6150ad1`](https://github.com/Sieboldianus/TagMaps/commit/6150ad16fcbf368aa7cd606954a92a4a27cac009))

* chore remove obsolete submodule init ([`eedee68`](https://github.com/Sieboldianus/TagMaps/commit/eedee6869e53fd2ad400f70e3aa51f2591e7fdd7))

* fix api links in contents ([`b1deea5`](https://github.com/Sieboldianus/TagMaps/commit/b1deea5846143c46ae98eb344f564b1d7bd6605a))

* cleanup pdoc and argdown ci job ([`8aa9869`](https://github.com/Sieboldianus/TagMaps/commit/8aa986966a44b92d45afe8b81c5fea0ebf94c558))

* Minor docs update to args ([`ebab129`](https://github.com/Sieboldianus/TagMaps/commit/ebab129a78dc94d3c00aff4b43561e878c5960c2))

* Merge branch &#39;apiref-docs-ci&#39; into dev ([`3c30a74`](https://github.com/Sieboldianus/TagMaps/commit/3c30a74dce772fee4d71891bde9cf3955150987d))

* fix warnings for empty modules in pdoc ([`f3936ce`](https://github.com/Sieboldianus/TagMaps/commit/f3936cef40abadcca318b1f9f7c6af679801e310))

* Update submodule argdown to latest ([`863ba91`](https://github.com/Sieboldianus/TagMaps/commit/863ba91bb7ab7d2963130f190b96e60caef5d506))


## v0.19.1 (2019-08-14)

### Fix

* fix: use correct column for cleaned output ([`f32d974`](https://github.com/Sieboldianus/TagMaps/commit/f32d974b0aff3a0aaa25b6c31b9cbf5ad4369065))

### Unknown

* Merge branch &#39;master&#39; of github.com:Sieboldianus/TagMaps ([`9bd57db`](https://github.com/Sieboldianus/TagMaps/commit/9bd57db35c98c857f9019239e428875348138916))


## v0.19.0 (2019-08-13)

### Chore

* chore: add mkdocs build instructions to gitlab-ci ([`22e3f39`](https://github.com/Sieboldianus/TagMaps/commit/22e3f3934b7d8174f25afc959a2a18da3593b117))

* chore: add mkdocs.yml instructions ([`7144a96`](https://github.com/Sieboldianus/TagMaps/commit/7144a96a9506110833fdd09cba5623da70f9fb86))

* chore: self-host conda-forge badge ([`69b5846`](https://github.com/Sieboldianus/TagMaps/commit/69b58461044f5a194673027bef7ccfa0ba660f89))

### Documentation

* docs: fix typo ([`d184885`](https://github.com/Sieboldianus/TagMaps/commit/d1848850b596ccd6327c9fc34e2abc56a41c5bf2))

* docs: add badge-links ([`126d9c0`](https://github.com/Sieboldianus/TagMaps/commit/126d9c0e0bcb23d1652c6cabb99b7b89bce7ba57))

* docs: restructure headings ([`d401887`](https://github.com/Sieboldianus/TagMaps/commit/d401887245c75b638f5730c4c06b8dcd3a67af38))

* docs: update future goals ([`97a24cd`](https://github.com/Sieboldianus/TagMaps/commit/97a24cdaed2f4ec0c946bfe0cacdd4e2548db606))

* docs: move from wiki to mkdocs

This commit adds a complete documentation, bundling all tagmaps related resources on a single [page](http://ad.vgiscience.org/tagmaps/docs) ([`b50c646`](https://github.com/Sieboldianus/TagMaps/commit/b50c646ae7228ee17550726dafadddd622cd15f4))

* docs: move documentation from wiki to mkdocs ([`964af12`](https://github.com/Sieboldianus/TagMaps/commit/964af12ee41b70c7a89437f53eed1923f647acdc))

* docs: update future goals ([`7eb7d27`](https://github.com/Sieboldianus/TagMaps/commit/7eb7d272d6172d31d80316c30c006015e71f93a7))

### Feature

* feat: allow multi-polygon shapefile intersection ([`32db42b`](https://github.com/Sieboldianus/TagMaps/commit/32db42ba6141908f47a7f5ee2ef44f49117dedfb))

### Fix

* fix: shapefile intersection for single polygons ([`9786a04`](https://github.com/Sieboldianus/TagMaps/commit/9786a04bcf19d39df91ee1d69197969324dff2f0))

* fix: include post_title in post selection

- improved filtering of characters in post_body column
- added funtions for cleaning up terms, numbers and characters (post_body)
- output_cleaned.csv now includes filtered wordlist from body ([`f9eecc3`](https://github.com/Sieboldianus/TagMaps/commit/f9eecc3606e3cb1d135f8c72ca886bb117f99922))

### Refactor

* refactor: compatibility for fiona 2.0 ([`a822107`](https://github.com/Sieboldianus/TagMaps/commit/a822107adc04b92d0f474972a9253989b4bbac9a))

### Unknown

* update SortOutAlways list ([`8c1e9d1`](https://github.com/Sieboldianus/TagMaps/commit/8c1e9d17a9328af93223a164c4a3fd3ffb83951c))

* Update mkdocs.yml

docs: change theory to concept ([`01d85a4`](https://github.com/Sieboldianus/TagMaps/commit/01d85a4ca45b17ed0b47798dee55b5bfc79d9a87))

* Update mkdocs badge generation ([`7e987e3`](https://github.com/Sieboldianus/TagMaps/commit/7e987e35e601e82d9ff40f31c119ec8bdceb73e9))

* Fix minor typo in figure caption ([`5942241`](https://github.com/Sieboldianus/TagMaps/commit/594224107a7227553102231db6cfad0ab20b0f23))

* Update badge links ([`9ffc6a1`](https://github.com/Sieboldianus/TagMaps/commit/9ffc6a13c3070ed3ba1e70193e6c02991ba9589f))

* fix main documentation link ([`4839054`](https://github.com/Sieboldianus/TagMaps/commit/48390546039e60611760a56f02728236fc16732d))

* Bump conda-forge recipe to latest version ([`bbb0f47`](https://github.com/Sieboldianus/TagMaps/commit/bbb0f47746ba489f5a09d3ebc9db572d68a93e68))


## v0.18.1 (2019-07-25)

### Documentation

* docs: add conda azure pipeline badge ([`1a01098`](https://github.com/Sieboldianus/TagMaps/commit/1a0109855df3c18cc543c0fee60440daf51d6408))

### Fix

* fix: return coordinates missing in _proj_coords ([`9cc0dfa`](https://github.com/Sieboldianus/TagMaps/commit/9cc0dfabe5b9154bd3b5b1e7ffa727bdcf2a91ce))

* fix: missing pyproj.Transformer for pyproj &lt;2.0.0 ([`9132d10`](https://github.com/Sieboldianus/TagMaps/commit/9132d104ec078e7c493fee8fa7280c8c4d2dac74))

### Unknown

* Bump conda-forge recipe to latest version&#34; ([`15933b9`](https://github.com/Sieboldianus/TagMaps/commit/15933b9e24c70cf89f7bd61edfd7ae8419af5097))


## v0.18.0 (2019-07-24)

### Chore

* chore: bump conda feedstock ([`c4ef16c`](https://github.com/Sieboldianus/TagMaps/commit/c4ef16c3c4378039f5466b5397f48fba13f28d71))

### Documentation

* docs(readme): add illustration of tagmaps steps ([`027945b`](https://github.com/Sieboldianus/TagMaps/commit/027945b610543dd1495fa5cd0241f62cd388197d))

* docs: add DOI for literature ref ([`2dd35b2`](https://github.com/Sieboldianus/TagMaps/commit/2dd35b270bf947962a2cff39157fd15afe91ae06))

* docs: add link to wiki install guide ([`565ce8d`](https://github.com/Sieboldianus/TagMaps/commit/565ce8d3ad56dc2af9d45e09f0b24892b7cbd198))

### Feature

* feat: add --version flag to args ([`0668b75`](https://github.com/Sieboldianus/TagMaps/commit/0668b75b641b788676087e9cbddd09f1f79814da))

### Fix

* fix: remove obsolete static column length check ([`301178e`](https://github.com/Sieboldianus/TagMaps/commit/301178ec0815596b63fd33d31a2347c98feb9039))

* fix: DepreciationWarning raised by hdbscan dependency ([`3fdcbb0`](https://github.com/Sieboldianus/TagMaps/commit/3fdcbb04bbb5e0e201443e900449184ea1df40d4))

### Refactor

* refactor: input args follow syntax conventions ([`bb8abce`](https://github.com/Sieboldianus/TagMaps/commit/bb8abce55097d14cc97a976aef37654e4baceed5))

* refactor: temporarily add six and joblib to fix hdbscan ([`fb31c8b`](https://github.com/Sieboldianus/TagMaps/commit/fb31c8b004a531811ad8bbef1fb2d1ff33f92c19))

### Unknown

* add deprecation warning for backwards compatibility ([`f4e362f`](https://github.com/Sieboldianus/TagMaps/commit/f4e362f5f171b6d1ba1ff26ccdc0b2ab4050616d))

* fix wording ([`34bd30d`](https://github.com/Sieboldianus/TagMaps/commit/34bd30d522faf305913929d4ef87d9ca9a3fa085))

* switch order in readme.md ([`d86c323`](https://github.com/Sieboldianus/TagMaps/commit/d86c323a3d52e6dbb6fea73ef4813fdd34ecc440))

* fix typo ([`c15a717`](https://github.com/Sieboldianus/TagMaps/commit/c15a7177b5803b1d98cf0fa4799cac7ca1472f9f))

* Minor readme formatting ([`3ff5bdb`](https://github.com/Sieboldianus/TagMaps/commit/3ff5bdbe50fe6dc9db32b9d247d838988e73a788))

* Update gitignore ([`635d918`](https://github.com/Sieboldianus/TagMaps/commit/635d918b13065844208b74840a13d00ca19e8968))

* Update link to wiki ([`c15979e`](https://github.com/Sieboldianus/TagMaps/commit/c15979e2f17d00343fc47f15eb0fead5bff1030b))


## v0.17.7 (2019-05-22)

### Chore

* chore: reduce version requirements for package dep ([`488c5bb`](https://github.com/Sieboldianus/TagMaps/commit/488c5bb88e2b3433660a8ac27ad25475b3f1bb14))

* chore: typo ([`ba187ce`](https://github.com/Sieboldianus/TagMaps/commit/ba187ce226db7b0e5c50d1cd0d360ea3f120d567))

* chore: update requirements.txt pyproj version ([`585c735`](https://github.com/Sieboldianus/TagMaps/commit/585c7353e7820129fa800625ab8387fffa9348cc))

* chore: update pyproj dependency ([`37f2fd7`](https://github.com/Sieboldianus/TagMaps/commit/37f2fd7c709813f1aa0cb0940b4408e64a4804c1))

### Documentation

* docs: add conda-forge reference ([`cdde4af`](https://github.com/Sieboldianus/TagMaps/commit/cdde4afda9e80e54844a7f76ceddbf74af5c01de))

* docs: update readme version and download link ([`a8b90a9`](https://github.com/Sieboldianus/TagMaps/commit/a8b90a9e5deacff934f96c4ea7a3c1d43bddfa14))

### Fix

* fix: file count reporting ([`45fd41f`](https://github.com/Sieboldianus/TagMaps/commit/45fd41f79d37a421f1636ea181b7b5fea2dc20f7))

* fix: add backwards compatibility for pyproj&lt;2.0.0 ([`8ef9da2`](https://github.com/Sieboldianus/TagMaps/commit/8ef9da27c29426dd6a90901ca97bbb8f28882466))

### Unknown

* Move staticfunctions to utilities ([`a54847c`](https://github.com/Sieboldianus/TagMaps/commit/a54847cc59489f33f4597a42842cc6b73d0c02c7))

* Clean Up comments ([`06143eb`](https://github.com/Sieboldianus/TagMaps/commit/06143eb0f19e5c4c18e556e46f2b34e05645db02))

* Update meta.yml ([`ce4734c`](https://github.com/Sieboldianus/TagMaps/commit/ce4734c6b9cd2922c015322c03d5d5057586b618))


## v0.17.6 (2019-05-13)

### Chore

* chore: update pyproj version in setup.py ([`b089cb3`](https://github.com/Sieboldianus/TagMaps/commit/b089cb34216481e1d715aefa53fdac1008708515))

* chore: update pyproj version for CI ([`3f6cffa`](https://github.com/Sieboldianus/TagMaps/commit/3f6cffaa5863d7b822e62271c1731fabbfafdb25))

* chore: use native conda paths for tcl dlls ([`98d7df4`](https://github.com/Sieboldianus/TagMaps/commit/98d7df46b888d720a18bb36f88a92721368f6ced))

* chore: add overwrite of pyproj folder ([`2f4709d`](https://github.com/Sieboldianus/TagMaps/commit/2f4709d94dbd2551f87b786f55bb96ac41715e2b))

* chore: add pyproj.datadir to cx_freeze includes ([`a2bcc29`](https://github.com/Sieboldianus/TagMaps/commit/a2bcc293272f13cc85efd2aadf7582975f666a78))

* chore: remove doc_url and dev_url from meta.yaml ([`0e4889c`](https://github.com/Sieboldianus/TagMaps/commit/0e4889c6665e0365aba1c6017aa66461b2178e1c))

* chore: add venv to gitignore ([`93b753e`](https://github.com/Sieboldianus/TagMaps/commit/93b753e44ecb91d91c800dfe11408d4384b159eb))

* chore: Update requirements.txt ([`c7bc523`](https://github.com/Sieboldianus/TagMaps/commit/c7bc523b12828a9ba85c1c82ccaf8ac40befb0e0))

* chore: clean up host requrements in meta.yml ([`afefefc`](https://github.com/Sieboldianus/TagMaps/commit/afefefc8e26243f8ed2c2d6d9d6e30a9a513470c))

* chore: update requirements.txt ([`2f59ddf`](https://github.com/Sieboldianus/TagMaps/commit/2f59ddfd95fbd49dcddb0a2a28a353a64a7a276e))

* chore: update pypi sha ([`5739e32`](https://github.com/Sieboldianus/TagMaps/commit/5739e32a3df1313d8b04c60c95e115f79d749959))

* chore: remove extra env file for dev-env ([`f44f101`](https://github.com/Sieboldianus/TagMaps/commit/f44f1016fc26de16fcc707af0d90da55ae58d88d))

### Documentation

* docs: version update ([`ae0a5c0`](https://github.com/Sieboldianus/TagMaps/commit/ae0a5c08568208eff8e2deec2836ebcb9d406d2f))

* docs: add anaconda cloud badge ([`cf88de4`](https://github.com/Sieboldianus/TagMaps/commit/cf88de40cda8bf28d42083422ff160477fa08517))

### Fix

* fix: geos.dll and geos_c.dll in cx_build ([`b9f2111`](https://github.com/Sieboldianus/TagMaps/commit/b9f2111a1dc426f72799fb31918807c488048165))

* fix: use transformer.transform for mass projection ([`ca8febc`](https://github.com/Sieboldianus/TagMaps/commit/ca8febcbe83c7404786a608c26b1244691b43a04))

### Unknown

* chore:fix cs_freeze mkl and pyproj issues ([`61fc74a`](https://github.com/Sieboldianus/TagMaps/commit/61fc74a8467a53352233cbc9046522d46b0e755f))

* Fix cx_freeze build issues ([`3151ec0`](https://github.com/Sieboldianus/TagMaps/commit/3151ec063c69642c73b67de7bbbac00701474ba4))

* Uncomment mkl ([`591f028`](https://github.com/Sieboldianus/TagMaps/commit/591f0284bbd50d3b8fd10a2ba8fae3fb96db6d1f))

* Revert &#34;chore: update requirements.txt&#34;

This reverts commit 2f59ddfd95fbd49dcddb0a2a28a353a64a7a276e. ([`e161cfd`](https://github.com/Sieboldianus/TagMaps/commit/e161cfd8083ddf65edfb783809544c500966459a))

* Merge branch &#39;dev&#39; of gitlab.vgiscience.de:ad/TagMaps into dev ([`1a97cb6`](https://github.com/Sieboldianus/TagMaps/commit/1a97cb67ed1fe8c9d838e0274e36a768bb34982f))

* Merge branch &#39;master&#39; into dev ([`f74ef21`](https://github.com/Sieboldianus/TagMaps/commit/f74ef21c9597cb47a66c6b04f49f3e17874379cb))


## v0.17.5 (2019-05-08)

### Chore

* chore: move pylint to conda deps ([`634ca51`](https://github.com/Sieboldianus/TagMaps/commit/634ca5141e4eb602da15c3b91522e81a40fcacde))

* chore: move pylint to conda deps ([`e04e731`](https://github.com/Sieboldianus/TagMaps/commit/e04e731c2119e4af79020ea85e32a89bdd2c8a56))

* chore: update env dependencies for gitlab-ci ([`d932637`](https://github.com/Sieboldianus/TagMaps/commit/d9326375d994e689271cc05eb0224478e65d05ad))

* chore: update conda meta.yml ([`3fc76b4`](https://github.com/Sieboldianus/TagMaps/commit/3fc76b4c474ed2894cee5c1ee51403208c1615a4))

* chore: remove placeholder sh files for conda bld ([`17ef359`](https://github.com/Sieboldianus/TagMaps/commit/17ef359c33dca672f14150b42f82d41110827a43))

* chore: clean up base env yml dependencies ([`d25ab9d`](https://github.com/Sieboldianus/TagMaps/commit/d25ab9d1a054d6d4310388338fc34727283f6065))

* chore: update dependencies with minimum versions ([`8fe455a`](https://github.com/Sieboldianus/TagMaps/commit/8fe455a16ae8e7903890ec52471e8356c19d47f8))

### Documentation

* docs(config): Update command line args info. ([`b59e083`](https://github.com/Sieboldianus/TagMaps/commit/b59e083ad42706d9c58a18c8ac98761cfe5e2832))

### Fix

* fix: console resize only for Windows os ([`1bbc64d`](https://github.com/Sieboldianus/TagMaps/commit/1bbc64d48fc90414ef8a09bcd3787bfc14fad993))

* fix: use correct dependency for attrs ([`72b63c0`](https://github.com/Sieboldianus/TagMaps/commit/72b63c059c5d02538e7c4951398967f18a6eeda9))

### Unknown

* Merge branch &#39;dev&#39; ([`e967245`](https://github.com/Sieboldianus/TagMaps/commit/e9672454df64ecb48f1db62a8df501e62d1883cf))

* Merge branch &#39;dev&#39; ([`bc17d3b`](https://github.com/Sieboldianus/TagMaps/commit/bc17d3b51c6b6c3daecf471aea3cad8ba9b929f5))

* Merge branch &#39;dev&#39; ([`8fa2ec8`](https://github.com/Sieboldianus/TagMaps/commit/8fa2ec838adb4207befe421dc799acb20ce0bf1a))

* Minor readme formatting ([`953258e`](https://github.com/Sieboldianus/TagMaps/commit/953258eda1d2ce4d8cdaa80fa3f3939ba33751ab))

* add api to write topic models ([`3d3102b`](https://github.com/Sieboldianus/TagMaps/commit/3d3102ba721352bf8330dbf6ea4ecb6d86d00512))

* Update version and build link (docs) ([`5f3e2c0`](https://github.com/Sieboldianus/TagMaps/commit/5f3e2c0a06352f7886b8b9667b1b240d0ff44c03))


## v0.17.4 (2019-03-08)

### Fix

* fix: add check for intermediate data ([`d6a24cd`](https://github.com/Sieboldianus/TagMaps/commit/d6a24cdcb92efe6139b1b9b7e7da0c24972094d9))


## v0.17.3 (2019-03-08)

### Fix

* fix: select only cluster shapes for projection ([`8db28f1`](https://github.com/Sieboldianus/TagMaps/commit/8db28f15b79af3ecfa488ccf26e42e37b3d708fa))

### Unknown

* Merge branch &#39;dev&#39; ([`097e0c8`](https://github.com/Sieboldianus/TagMaps/commit/097e0c8e6606c0f2c9e6a181ac7ac38d37007fdc))

* Added arcgis mxd layout files for different versions ([`b0556d2`](https://github.com/Sieboldianus/TagMaps/commit/b0556d2df21121e446c01612fddf68cabe16b02d))

* follow conventions ([`8466b64`](https://github.com/Sieboldianus/TagMaps/commit/8466b64f7deb07a43b817219a83353c6bec8bdab))

* refactor of Alpha Shapes output to namedtuple ([`73b9421`](https://github.com/Sieboldianus/TagMaps/commit/73b9421a9c278afa053cd517192cafae30683df9))

* minor fix pipe ([`108fda9`](https://github.com/Sieboldianus/TagMaps/commit/108fda9ffb7b6b522b683d9c0602b389d0453f42))


## v0.17.2 (2019-02-26)

### Documentation

* docs: added background info regarding post structure and metrics ([`de5d7d7`](https://github.com/Sieboldianus/TagMaps/commit/de5d7d74772df0f7883b005d0caef3f1111862b7))

### Fix

* fix(docs): readme links ([`13a9f29`](https://github.com/Sieboldianus/TagMaps/commit/13a9f2926f30454f47f99bfe1d1e47c5f9cd9eda))

### Unknown

* improve handling of cluster centroid data ([`9f66744`](https://github.com/Sieboldianus/TagMaps/commit/9f6674431862eeba98207a95dbc6848f1096aecb))

* update repo links in readme ([`218cdc0`](https://github.com/Sieboldianus/TagMaps/commit/218cdc01d43483cef2c09c1742a7b123a043999a))

* update cleaned data output args ([`dbc8cde`](https://github.com/Sieboldianus/TagMaps/commit/dbc8cde756bf4ed5bb4084466ed67a6d566b1329))

* refactor method rectangle bounds, add namedtuple ([`72b8c8c`](https://github.com/Sieboldianus/TagMaps/commit/72b8c8c7823284b7a15952ee6dde4f027e0365b0))

* fixup! Fix yml error ([`ae580d7`](https://github.com/Sieboldianus/TagMaps/commit/ae580d72cb58d00d2bd1c4d3e92904885edaab3a))

* fixup! Fix yml error ([`8b920ec`](https://github.com/Sieboldianus/TagMaps/commit/8b920ecfaa47f160cda587826e0da8114ca23650))

* fixup! Fix yml error ([`6f0a27a`](https://github.com/Sieboldianus/TagMaps/commit/6f0a27a3c1424ef50f6c80c26f36202cb01ea8b3))

* fixup! Fix yml error ([`818fc63`](https://github.com/Sieboldianus/TagMaps/commit/818fc636cc747a845dfcc80429bdcad8a2f8e4f1))

* fixup! Fix yml error ([`8a0e080`](https://github.com/Sieboldianus/TagMaps/commit/8a0e0803595300156e83f057b78dff2626c47670))

* Fix yml error ([`132bfed`](https://github.com/Sieboldianus/TagMaps/commit/132bfed777d3f5881172c5a3ae2b3cfc64677f78))

* Fix CI relative path ([`80a4421`](https://github.com/Sieboldianus/TagMaps/commit/80a442176daa81ffbe50076aa1b4f6e42265e99f))

* Fix CI path ([`2dc12c9`](https://github.com/Sieboldianus/TagMaps/commit/2dc12c9444044e53d15a45cc99f8a25b765dfb6e))

* Minor doc update ([`736eaaa`](https://github.com/Sieboldianus/TagMaps/commit/736eaaadd10b343af71a6a8cf4010c44e6085193))


## v0.17.1 (2019-02-25)

### Fix

* fix: use filtered example data for system integration test ([`13f91c8`](https://github.com/Sieboldianus/TagMaps/commit/13f91c83b942cc13fa2ef8b39f31de6a2ad853f7))

* fix: tagmaps example image link on pypi ([`08aad43`](https://github.com/Sieboldianus/TagMaps/commit/08aad4303fafafbc3533d0c293f94721b24c157d))

### Unknown

* Merge branch &#39;dev&#39; ([`3bb688b`](https://github.com/Sieboldianus/TagMaps/commit/3bb688b9113cc42dbf034d0166b63206fb91f08d))

* minor style refactor ([`ac7b2df`](https://github.com/Sieboldianus/TagMaps/commit/ac7b2df60ea77bb851dc952ab7fc2c92fd127191))


## v0.17.0 (2019-02-25)

### Feature

* feat: anonymize intermediate data based on global term occurence ([`ac89d10`](https://github.com/Sieboldianus/TagMaps/commit/ac89d107bb172661e394c95017f6e5fda0d1885d))

### Style

* style: major code style overhaul, fixed convention warnings ([`8c8cba3`](https://github.com/Sieboldianus/TagMaps/commit/8c8cba336b0f3d354a3f9549282b3bb7c3314d64))

* style: cleaned imports in all files ([`1b16dee`](https://github.com/Sieboldianus/TagMaps/commit/1b16dee3730fffeacbfc42309bf79ab38e4287e4))

### Unknown

* Merge branch &#39;dev&#39; ([`87d6d63`](https://github.com/Sieboldianus/TagMaps/commit/87d6d63f4759c7485d7ebff4b52f52dfdcad6d17))

* update gitignore ([`edfda6a`](https://github.com/Sieboldianus/TagMaps/commit/edfda6a6f3fa83f084a07aad28a05ee223d40afe))

* commented panon feature ([`cadb338`](https://github.com/Sieboldianus/TagMaps/commit/cadb3382b2a1eee415f47086000438725f86acda))

* add get pseudo-anonymized cleaned post dict method ([`81de8cb`](https://github.com/Sieboldianus/TagMaps/commit/81de8cb17173b04f329841385aef93ac870c8cd5))

* removed uneccesary imports ([`653026c`](https://github.com/Sieboldianus/TagMaps/commit/653026cb26d020db07e162a8ebdeb47b7fa43a84))

* minor refactor name-tuple-ref&#39;s ([`563f955`](https://github.com/Sieboldianus/TagMaps/commit/563f955701e436f843790c1a2a3116e7260cec3c))


## v0.16.0 (2019-02-22)

### Feature

* feat: load data from intermediate results ([`9e8af98`](https://github.com/Sieboldianus/TagMaps/commit/9e8af983f553ffb8e17d94e5ecd0504ecea7c777))

* feat: add option to load intermediate (cleaned) data ([`ca522f0`](https://github.com/Sieboldianus/TagMaps/commit/ca522f06882b22c19af7275dcf01564186b45e18))

* feat: add method to get cluster centroid figure ([`351fbf1`](https://github.com/Sieboldianus/TagMaps/commit/351fbf1ffa8418eb6d20308a6649569bfd0f3e7a))

### Fix

* fix: extract distinct emoji (remove duplicates) ([`ae23464`](https://github.com/Sieboldianus/TagMaps/commit/ae234640e8e11cbaf656c1cc52f5ece823e2b75a))

### Refactor

* refactor(prepare_data): parametrize cls_type for item stats ([`db8d1d3`](https://github.com/Sieboldianus/TagMaps/commit/db8d1d39dace67b9400a8a3371635179fdcfeb9f))

* refactor: add decorator for checking topic terms ([`6d0748d`](https://github.com/Sieboldianus/TagMaps/commit/6d0748d823c78cb8dfd263d5ea8db0e9e1a5234d))

### Unknown

* fix  to process all toplists ([`4cdbee1`](https://github.com/Sieboldianus/TagMaps/commit/4cdbee173d6c52a9fa3846a58f1999bfe6477d4f))

* major refactor of prepared data structure ([`5b15ef5`](https://github.com/Sieboldianus/TagMaps/commit/5b15ef5c11694018dba5a2c35adfa76017825ae7))

* refactor several tuple-results into namedtuple ([`6d3caba`](https://github.com/Sieboldianus/TagMaps/commit/6d3caba4b6788c229f66eaf3683ee4fbce459852))

* fixup! refactor(prepare_data): parametrize cls_type for item stats ([`c1de7f0`](https://github.com/Sieboldianus/TagMaps/commit/c1de7f0e0025187d2265a16ee8082c0b2f9462b7))

* fixup! Initial feat for cleaned data load (not ready) ([`729acb7`](https://github.com/Sieboldianus/TagMaps/commit/729acb78be7245f8055260bf82222769b68b5c5c))

* Initial feat for cleaned data load (not ready) ([`f8166f6`](https://github.com/Sieboldianus/TagMaps/commit/f8166f6485f357617ef98b736ee6a7438005ced5))

* fixup! refactor: add decorator for checking topic terms ([`2b8058f`](https://github.com/Sieboldianus/TagMaps/commit/2b8058ff04e8c299020480ea7dfffd92b382efab))

* use concat term list for handling topics ([`9578c57`](https://github.com/Sieboldianus/TagMaps/commit/9578c572bf6cc235aa491bea84d995dce192fe7b))

* update changelog ([`ebca020`](https://github.com/Sieboldianus/TagMaps/commit/ebca0202f086f81115f8f11da28064c31778ae92))


## v0.15.0 (2019-02-19)

### Documentation

* docs: minor spelling ([`4d91baf`](https://github.com/Sieboldianus/TagMaps/commit/4d91bafbc3c389cbc70245f50cdf161376c898f6))

### Feature

* feat: add topic clusterer ([`4694157`](https://github.com/Sieboldianus/TagMaps/commit/469415789b7d6e73ffd75205bcb093e2f3034e91))

### Fix

* fix: bool-alpha issue ([`3a833f8`](https://github.com/Sieboldianus/TagMaps/commit/3a833f84253b012b04d2cd0efa1126bd0d593897))

* fix: output reporting emoji bug ([`33a4583`](https://github.com/Sieboldianus/TagMaps/commit/33a45838f9fb419020c310d05d82feba893595b6))

* fix: alpha shapes not returned for some cluster point clouds ([`c43d86f`](https://github.com/Sieboldianus/TagMaps/commit/c43d86f7bc1ebd710795e34fee0ac08c3e9e5fbd))

### Refactor

* refactor: separate plotting and interface methods

- use object oriented matplotlib where possible
- bugfixes to display in jupyter inline and interactive mode
- allow retrieving figures separately from interface ([`4f98259`](https://github.com/Sieboldianus/TagMaps/commit/4f9825936a77799513b8d514e3074afe3fa20273))

* refactor: use decorators for checking states in main api ([`0da3d6c`](https://github.com/Sieboldianus/TagMaps/commit/0da3d6c9c87a9445fe4718b01c56a06df47564b8))

* refactor: move plotting methods to separate class ([`037be50`](https://github.com/Sieboldianus/TagMaps/commit/037be50d409b5aced7351da57de8166fae50595c))

* refactor: system integration test ([`984e011`](https://github.com/Sieboldianus/TagMaps/commit/984e0117d645d4d1406521404cbc28f2dfd843b9))

### Style

* style: remove obsolete comments from code ([`2b7da3c`](https://github.com/Sieboldianus/TagMaps/commit/2b7da3c20e561cb157179686910e424088a50b67))

* style(main): code style improvements ([`e731587`](https://github.com/Sieboldianus/TagMaps/commit/e7315877104c5aae44b0f0d13ef77b848317ba66))

### Unknown

* code style improvements, reporting ([`24d586c`](https://github.com/Sieboldianus/TagMaps/commit/24d586c55585117b6e3cfdc4ec2a3a097e94440a))

* Merge branch &#39;dev&#39; of gitlab.vgiscience.de:ad/TagCluster into dev ([`e2439e5`](https://github.com/Sieboldianus/TagMaps/commit/e2439e5d9ffaab55375b08292495f299570e8d4d))

* refactor cluster process methods ([`9fc57e8`](https://github.com/Sieboldianus/TagMaps/commit/9fc57e852e754a302954f5962a125ee0616b00e8))

* Restrict gitlab-ci Pipeline to master ([`0f13ab5`](https://github.com/Sieboldianus/TagMaps/commit/0f13ab5ff922d8452a5dccb671fcbdaa9d9cb06b))

* refactor cluster map gen methods ([`35ac0f5`](https://github.com/Sieboldianus/TagMaps/commit/35ac0f5094c93bedb212d0645a138a5018152cb4))

* Merge branch &#39;master&#39; into dev ([`79a4fcf`](https://github.com/Sieboldianus/TagMaps/commit/79a4fcf6307bc3f8e44f4e76a93ec5b22821aeca))

* conda receipe start ([`4096038`](https://github.com/Sieboldianus/TagMaps/commit/40960383f34d2265b0c721129dc77d43ae7a0486))

* code style ([`4c188f2`](https://github.com/Sieboldianus/TagMaps/commit/4c188f2b1116576de4d8554ec0a74edc1f889fc0))

* fix cx build process ([`50fb60b`](https://github.com/Sieboldianus/TagMaps/commit/50fb60b6b4c79d904de01862ba1142b26932113f))

* filter sklearn depreciation warning from joblib import ([`3b56d49`](https://github.com/Sieboldianus/TagMaps/commit/3b56d49cc842ac47f1abf2e0adeb01d93f1d7165))

* fixup! fix ci pipeline ([`711634f`](https://github.com/Sieboldianus/TagMaps/commit/711634f23f1ec4d4cef6bb5e4ef7a406e309b22c))

* fixup! fix ci pipeline ([`9a975c3`](https://github.com/Sieboldianus/TagMaps/commit/9a975c31a4e52ac3713ede4134168adb85babd22))

* fixup! fix ci pipeline ([`a0228e8`](https://github.com/Sieboldianus/TagMaps/commit/a0228e85cde4f84a18afeeb1d5382e869705572a))

* fixup! fix ci pipeline ([`43bb93d`](https://github.com/Sieboldianus/TagMaps/commit/43bb93dbc5f4d795ce31b001ba0a8ce7f279c4fd))

* fix ci pipeline ([`ed7e568`](https://github.com/Sieboldianus/TagMaps/commit/ed7e56843dae1906dff34ec036c66802bf56b8bd))

* fixup! main test ci fixes ([`e0eae46`](https://github.com/Sieboldianus/TagMaps/commit/e0eae4680f77ad7b6cf81909689a3b2edeaa4c19))

* fixup! main test ci fixes ([`1acb616`](https://github.com/Sieboldianus/TagMaps/commit/1acb61625cd9f61193260a08dbac8d25078c2469))

* main test ci fixes ([`fa85873`](https://github.com/Sieboldianus/TagMaps/commit/fa858732f7a00537cbaf79fa8460c6fac5941257))

* update for main integration test in gitlab-ci ([`f627220`](https://github.com/Sieboldianus/TagMaps/commit/f627220f2be6bde909a23f187d22e82cf7e7c13e))

* fixes for cx_setup.py in windows ([`cf9f288`](https://github.com/Sieboldianus/TagMaps/commit/cf9f288fd4f394aedde715cded16b111dfe0ea2c))


## v0.14.0 (2019-02-11)

### Chore

* chore: cleanup dependency files ([`c5391f8`](https://github.com/Sieboldianus/TagMaps/commit/c5391f816c8a1cd560b3b892bdf312b6f25e7172))

* chore: set minimum pandas version to 0.24.0 due to .to_numpy() use ([`7a878ea`](https://github.com/Sieboldianus/TagMaps/commit/7a878ea656ee030845dda8076c6b3ae0eb3ebcfb))

* chore: fix logging for Jupyter Notebook mode ([`11cc9f4`](https://github.com/Sieboldianus/TagMaps/commit/11cc9f45753101afa6d53c3eff3ef733acbf0603))

* chore: improve logging ([`05e5a90`](https://github.com/Sieboldianus/TagMaps/commit/05e5a9088a436a2320ca47e72dbbd4fbde20692e))

* chore: add verbose logging flag ([`fc27e61`](https://github.com/Sieboldianus/TagMaps/commit/fc27e61f1898c5b7fa15722984789bb077c5c251))

### Feature

* feat: add public api for selection preview map ([`8e10cf8`](https://github.com/Sieboldianus/TagMaps/commit/8e10cf81559da7d5008663605e81effeedac84df))

### Style

* style: allow use of base config on import ([`85593e2`](https://github.com/Sieboldianus/TagMaps/commit/85593e24a8ef3fbe79f75aa63bb5b00eb4fef5fe))

### Unknown

* Move pyproj for ci to conda list ([`c70dd47`](https://github.com/Sieboldianus/TagMaps/commit/c70dd47d70acf5b06ca8ab574c3fab81ec8b2da9))

* update ci-yml ([`59cb582`](https://github.com/Sieboldianus/TagMaps/commit/59cb582c1d7263dd61a16767ed4f8342fc279ca3))

* add conda receipe folder to gitignore ([`9dc219c`](https://github.com/Sieboldianus/TagMaps/commit/9dc219c10a6a0d69d610c16b890dd4432ee1e06e))

* fix depreciation warning for hdbscan dependencies

- also fix pyproj error by installing from pip instead
of conda ([see](https://github.com/jswhit/pyproj/issues/134) ([`981168a`](https://github.com/Sieboldianus/TagMaps/commit/981168ae74918fdca057b6d94f864560ff4fa19e))

* Merge branch &#39;master&#39; of gitlab.vgiscience.de:ad/TagCluster ([`008122e`](https://github.com/Sieboldianus/TagMaps/commit/008122e78b9d302446a57da0a739ada693791a6b))

* cleanup code comments ([`11d49af`](https://github.com/Sieboldianus/TagMaps/commit/11d49af61cd5494cb25bc56e77d4556fc077372a))

* Added conda env steps to readme ([`6857817`](https://github.com/Sieboldianus/TagMaps/commit/68578172d130e19b5d35c8dd4d0cc8c5c7c586ed))

* fixup! Update readme ([`901192d`](https://github.com/Sieboldianus/TagMaps/commit/901192dd7a10a21bc043eb73ef56ee9c2faed38a))

* Update readme ([`110b45d`](https://github.com/Sieboldianus/TagMaps/commit/110b45d9a4e786e0f5ac1c84dfdc677df7c9d210))

* Added gitlab-ci pipeline and badge generation&#34; ([`e600871`](https://github.com/Sieboldianus/TagMaps/commit/e600871e35b51c7402af914ca07035a8cae656ea))

* remove global tnum ([`00c48ad`](https://github.com/Sieboldianus/TagMaps/commit/00c48adc6879514d4bc8b6d02cae6ba095ee1d9a))

* change tagmaps.clusterer from list to dict for  direct access ([`319eaed`](https://github.com/Sieboldianus/TagMaps/commit/319eaedae84f2776477f8719a8839084f5bf1671))


## v0.13.2 (2019-02-07)

### Documentation

* docs: update readme with tutorial link ([`70ef45f`](https://github.com/Sieboldianus/TagMaps/commit/70ef45fbb1bfb58993a960d26ed7f52600598581))

### Fix

* fix: update __init__.py and package structure for proper import ([`3a11f19`](https://github.com/Sieboldianus/TagMaps/commit/3a11f1933ce4f6aca8e8d0c7cfb194513f397983))

### Unknown

* style fix ([`f373a78`](https://github.com/Sieboldianus/TagMaps/commit/f373a782a7a4827faa92e79b456b30bdb26fe2c0))

* Added links to paper ref PDF ([`a1a780b`](https://github.com/Sieboldianus/TagMaps/commit/a1a780b9390237f16f679c014f9a2a464f8c99d7))

* Added paper refs ([`e5180e8`](https://github.com/Sieboldianus/TagMaps/commit/e5180e8abeb1ef53f94d1d3e2b8fbc5559126ee1))

* Add presentation link ([`49e16b0`](https://github.com/Sieboldianus/TagMaps/commit/49e16b0921077808c6c8fbef0489cf0e3d462a8a))

* include radon for code metrics in dev mode ([`4271dbc`](https://github.com/Sieboldianus/TagMaps/commit/4271dbcb5fc85ecfb075d8d8dc50739b8823c610))

* add option to filter for data origin ([`213b6d6`](https://github.com/Sieboldianus/TagMaps/commit/213b6d6114c1c73cea7349533e8dff24a9cdde9e))

* Add pypi badge ([`a1be586`](https://github.com/Sieboldianus/TagMaps/commit/a1be586724a59e87497369dada4461da1a63f0a8))

* update build name in cx_freeze ([`28e1dc3`](https://github.com/Sieboldianus/TagMaps/commit/28e1dc3d2f00df5953a7edbf3b2cf3325972448c))


## v0.13.1 (2019-02-06)

### Fix

* fix(main): move package direct hook to end of file ([`542e911`](https://github.com/Sieboldianus/TagMaps/commit/542e9110594d15ef252ad1563dc6aaeffdb5ca63))

### Unknown

* Auto rename for Pool.pyc in cx_freeze setup ([`7a28f91`](https://github.com/Sieboldianus/TagMaps/commit/7a28f91e0a35b663df438b86881afc43dc70ee42))

* add new version information with changelog ([`e43ef40`](https://github.com/Sieboldianus/TagMaps/commit/e43ef4043c857c333824d73930fece002aee9141))


## v0.13.0 (2019-02-06)

### Chore

* chore: update pipfile, add to repo ([`b48bea3`](https://github.com/Sieboldianus/TagMaps/commit/b48bea3668c925ab6751ec518cc5f1fc029c6848))

### Documentation

* docs: fix releases link ([`90ee006`](https://github.com/Sieboldianus/TagMaps/commit/90ee006bf4791afab292e72c898193cfbc90ec24))

### Feature

* feat: add public API for import of package ([`6b5ba86`](https://github.com/Sieboldianus/TagMaps/commit/6b5ba86892e8a8d952ef769c215be62332c052dc))

### Refactor

* refactor:  load data and prepare data into separate classes ([`c9d129c`](https://github.com/Sieboldianus/TagMaps/commit/c9d129c7a661bd0665012dae4f9dbeb9d07baa11))

### Style

* style: use Pathlib for output paths ([`cefa0e1`](https://github.com/Sieboldianus/TagMaps/commit/cefa0e193b1e6c2b311b55c93c4d3bd6f04e5212))

### Unknown

* add prepare_data class (placeholder) ([`57899d1`](https://github.com/Sieboldianus/TagMaps/commit/57899d1c503240ddc8f51b374725ee502a0af5ce))

* Update readme ([`7509c3b`](https://github.com/Sieboldianus/TagMaps/commit/7509c3b622f3dcb3dc38cc4b7431cb9cb0f9512a))

* Remove vscode settings.json from git ([`8d0e9f4`](https://github.com/Sieboldianus/TagMaps/commit/8d0e9f41b7e8a1a564d478e7eb56ee180c5940b1))

* fix gitignore line endings ([`0f98437`](https://github.com/Sieboldianus/TagMaps/commit/0f984374e7133754b136bb23e2a52b55813642f8))

* Update readme ([`126ca59`](https://github.com/Sieboldianus/TagMaps/commit/126ca59b02798a06e0fbcd263b85e7e546c5658c))

* remove sys from import ([`de670bb`](https://github.com/Sieboldianus/TagMaps/commit/de670bb668c82e37fceda12205aa269d5f09ce6e))


## v0.12.2 (2019-01-29)

### Fix

* fix: correct empty bounds report ([`1bde961`](https://github.com/Sieboldianus/TagMaps/commit/1bde9613912dce5e996acaa32a347806415d02d1))

* fix(interface): clusterer reference ([`9b8dbd8`](https://github.com/Sieboldianus/TagMaps/commit/9b8dbd8837466884c3477b49793991b08f19e5f9))

### Unknown

* Update ArcMap mxd ([`3b8bfff`](https://github.com/Sieboldianus/TagMaps/commit/3b8bfff677dfba140c8a1d159f7fa67bee21d8e1))

* Add readme to Flickr Sample data ([`a04124d`](https://github.com/Sieboldianus/TagMaps/commit/a04124d59782c61a66ae620d5c26fa2409ca22b8))


## v0.12.1 (2019-01-29)

### Documentation

* docs: add sample data

This includes sample data from Flickr
which was published using CC-BY-Licenses:
https://www.flickr.com/services/api/flickr.photos.licenses.getInfo.html
(includes licenses 1, 2, 3, 5, 6, 7, 9, and 10) ([`1a6157e`](https://github.com/Sieboldianus/TagMaps/commit/1a6157e0723bda3580bce8716afd7ed463f041ad))

* docs: update readme and ref to main repo ([`5518f08`](https://github.com/Sieboldianus/TagMaps/commit/5518f0876ddef46e4a3379aea6440e5c22f0565b))

### Fix

* fix: skip empty shapes on output ([`c4e105e`](https://github.com/Sieboldianus/TagMaps/commit/c4e105efab5f723365ef7be917b298fb9446bd4a))

* fix: catch empty top_list ([`b5b4a5e`](https://github.com/Sieboldianus/TagMaps/commit/b5b4a5e0fd876d19ea2d17d9f5349b2e4980d362))

* fix: empty records loop ([`5c25c39`](https://github.com/Sieboldianus/TagMaps/commit/5c25c39a127e80011a6a11bcadbb245d404b2ce4))


## v0.12.0 (2019-01-29)

### Chore

* chore: update cx_freeze setup to pipenv ([`95c5e19`](https://github.com/Sieboldianus/TagMaps/commit/95c5e19b3df272f1963ed05fcd455494bd9fc2fe))

### Documentation

* docs: update readme ([`1b3b4a5`](https://github.com/Sieboldianus/TagMaps/commit/1b3b4a5a2ea968ffd9f7e1e30eb9a7348f60f60e))

### Feature

* feat: enable pypi upload for semantic-release ([`593975f`](https://github.com/Sieboldianus/TagMaps/commit/593975f527a16c5c92c82d31e8c192610636de02))

### Refactor

* refactor: remove obsolete files and move deployment to resources ([`822e9df`](https://github.com/Sieboldianus/TagMaps/commit/822e9df09e3180aa046acc2ca013d45611631a7d))

### Unknown

* remove empty line ([`da44c6f`](https://github.com/Sieboldianus/TagMaps/commit/da44c6fc35bbe3a0f05f23738a4dd72737e51ccf))

* fix cx_freeze setup and missing dlls ([`2ba8691`](https://github.com/Sieboldianus/TagMaps/commit/2ba8691a44232e2b1e46ca8320152cf552642571))

* develop dependency; cx_Freeze ([`ded0591`](https://github.com/Sieboldianus/TagMaps/commit/ded05919823f1cf05b4b612a823bc961b61e385f))

* update filelists ([`ddc10f1`](https://github.com/Sieboldianus/TagMaps/commit/ddc10f14408555ad0b56b087e3671ef24b6d2e3d))

* refactor code style ([`b2f345c`](https://github.com/Sieboldianus/TagMaps/commit/b2f345c425fa46f937db681a737c2969f6108bcb))

* Removed files from VsiaulStudio ([`e472dc9`](https://github.com/Sieboldianus/TagMaps/commit/e472dc90e928492a5df33d833aa8a3b2ed977668))


## v0.11.1 (2019-01-29)

### Documentation

* docs: updated readme ([`e651ff8`](https://github.com/Sieboldianus/TagMaps/commit/e651ff825abea3def8d27a565cf804c77f29e22c))

### Fix

* fix: alternative for unicodedata emoji name not found ([`4c06210`](https://github.com/Sieboldianus/TagMaps/commit/4c062103546e759334de2a0fa20206858967071a))

* fix: explicit import of tkinter error ([`a19e637`](https://github.com/Sieboldianus/TagMaps/commit/a19e6377d9db9e7a793cf26dfe0b0e93131ed168))

* fix: conversion of dataframe to numpy.ndarray with column selection ([`0c0daef`](https://github.com/Sieboldianus/TagMaps/commit/0c0daef27766a8952429e96415231bf40e581663))

* fix: update list of dependencies ([`4a3ce89`](https://github.com/Sieboldianus/TagMaps/commit/4a3ce89c7a308cb489946abb0760a2bda86326e0))

* fix: input args handling (flags) ([`ef649eb`](https://github.com/Sieboldianus/TagMaps/commit/ef649ebff3dc0ddfc385970f10453cb74d471698))

* fix: handle input arg for local saturation check correctly ([`dcfe1cf`](https://github.com/Sieboldianus/TagMaps/commit/dcfe1cf710cd4c10e8243686dc77f434fb607aa4))

* fix(cluster): allow disable local saturation check ([`65d3a60`](https://github.com/Sieboldianus/TagMaps/commit/65d3a60e225fcb27a247c4ec997cb5912fce99bc))

### Style

* style: suppress  depreciationwarning for hdbscan module ([`429ee97`](https://github.com/Sieboldianus/TagMaps/commit/429ee97ba4e0aceba340c2b6de67d564d718ac07))

* style: updated docstring ([`1891c85`](https://github.com/Sieboldianus/TagMaps/commit/1891c85c943622785887eca4164f3df553393209))

* style: update setup and cx_freeze code formatting ([`e81ded7`](https://github.com/Sieboldianus/TagMaps/commit/e81ded7bc1bb7759ac08720e643ce8a1076279b7))

* style: increase location saturation default from 60 to 80% ([`bc92401`](https://github.com/Sieboldianus/TagMaps/commit/bc92401c08a609b16ba467d0e496914b972f27be))

### Unknown

* refactor obsolete code ([`2c6c04a`](https://github.com/Sieboldianus/TagMaps/commit/2c6c04a77b1750f549735796027f5151e689069f))

* code style update ([`05f8a57`](https://github.com/Sieboldianus/TagMaps/commit/05f8a575eb616dc48c2ce19b81401e5a9c27ce68))

* add optional args processing to load_data ([`a001a2a`](https://github.com/Sieboldianus/TagMaps/commit/a001a2ab4f1ba92a23d8baa239b2078e3b8888f3))

* add gdal to list of dependencies, required for fiona ([`3c69048`](https://github.com/Sieboldianus/TagMaps/commit/3c69048f08bb061e7253bb56b9022cceb1947643))

* use values instead of as_matrix, as suggested from futurewarning

FutureWarning: Method .as_matrix
will be removed in a future version.
Use .values instead. ([`95bafc8`](https://github.com/Sieboldianus/TagMaps/commit/95bafc88eb9939b3bfe6b40cbec65676ac697c84))

* update pipfile ([`d75cfd7`](https://github.com/Sieboldianus/TagMaps/commit/d75cfd7591a703dc67af773f8a7a9f9c03425050))

* virtualenv path ([`6031929`](https://github.com/Sieboldianus/TagMaps/commit/60319291bddfb9b375d428fcb316d9f5527b711f))

* ignore false positive form pylint ([`ac884d7`](https://github.com/Sieboldianus/TagMaps/commit/ac884d75aaadd0e812ba3c6fffa81f579469d351))

* add pipfile to gitignore according to [1]

https://github.com/pypa/pipenv/issues/1911 ([`3913f1f`](https://github.com/Sieboldianus/TagMaps/commit/3913f1f2d914ad678461a5f50e979aac335e6ebb))

* add newline comment ([`1782575`](https://github.com/Sieboldianus/TagMaps/commit/1782575ed0d9e9a22d2765d48ac21e0530e23ef1))

* add newline empty to emoji writer ([`9c537eb`](https://github.com/Sieboldianus/TagMaps/commit/9c537eb0755c93ec08c02140e6ac6872cafa230e))

* clean cmd scripts with obsolete args list ([`d6aae55`](https://github.com/Sieboldianus/TagMaps/commit/d6aae556d91ea4f999067143489f7565f0d935bc))

* fix dynamic package paths ([`3c29edc`](https://github.com/Sieboldianus/TagMaps/commit/3c29edcd6cd14deb9692751aacdef687450a6c66))

* update emoji csv output ([`f034e71`](https://github.com/Sieboldianus/TagMaps/commit/f034e7107b2021b9e4dff09157971e65b3af205d))

* fix (update) arg formatting in cmd scripts ([`5c1b802`](https://github.com/Sieboldianus/TagMaps/commit/5c1b80240807829c94dc23197b37d41b3c77f672))

* Revert &#34;remove obsolete emoji csv output and sort shapefile based on weights&#34;

This reverts commit 6b16376ec03a262844438cf34e739dc6b40d6c12. ([`a2f2d0c`](https://github.com/Sieboldianus/TagMaps/commit/a2f2d0c9e486780120afff356c7351768aab2c86))

* remove obsolete emoji csv output and sort shapefile based on weights

instead of first column ([`6b16376`](https://github.com/Sieboldianus/TagMaps/commit/6b16376ec03a262844438cf34e739dc6b40d6c12))

* fix top_tag selection for local saturation check ([`210b781`](https://github.com/Sieboldianus/TagMaps/commit/210b781d832c6243ffcf2b71a8be8e052326f8cb))

* fix process for partial clustering tags, emoji or locations ([`3107999`](https://github.com/Sieboldianus/TagMaps/commit/3107999b2ef51ea7e22665e771a9e821c29f32b1))

* add linebreak ([`95a5f5b`](https://github.com/Sieboldianus/TagMaps/commit/95a5f5ba94ffdb269f39cc7f4ee85740196dc6ec))

* update default value for local saturation check (now false) ([`08f15d0`](https://github.com/Sieboldianus/TagMaps/commit/08f15d0222da115be3f676980b9597ea2cd45900))

* add dev folde rto gitignore ([`4c7dca1`](https://github.com/Sieboldianus/TagMaps/commit/4c7dca11cde18c5fbaa8c07c92f96de123e7852e))


## v0.11.0 (2019-01-23)

### Chore

* chore: add lbsntransform to dependencies ([`4fd83a4`](https://github.com/Sieboldianus/TagMaps/commit/4fd83a4b38275e04763a7edae84e74c36caed583))

### Feature

* feat: allow removing posts from processing list based on location ([`325cd6b`](https://github.com/Sieboldianus/TagMaps/commit/325cd6b46747693bb67e10e12b73200c8ee61bec))

* feat: add location filter function ([`987ba4e`](https://github.com/Sieboldianus/TagMaps/commit/987ba4e6f688c6b2f747e1017c8bb6b4934a2ce6))

* feat: replace csv.Reader with csv.DictReader

- allows accessing fields by name, ignoring order
- allows using get with default (None) values for missing attributes ([`c1782f9`](https://github.com/Sieboldianus/TagMaps/commit/c1782f94efe03dcb4a44496df51d504b722b4277))

### Fix

* fix: emoji extration from string with recognizing grapheme clusters ([`a1fae93`](https://github.com/Sieboldianus/TagMaps/commit/a1fae937c50f51a266009a78c6e6086048417a6a))

* fix: delete key in list with reference by value ([`544708b`](https://github.com/Sieboldianus/TagMaps/commit/544708bb772b98cfbc275544c074e5680476ad5a))

* fix: long tail length removal reporting ([`3131d4a`](https://github.com/Sieboldianus/TagMaps/commit/3131d4aff2fd4d5e94b818fe0c7fdd041a9ceb3e))

### Refactor

* refactor: improve shared structure throuout project ([`866314b`](https://github.com/Sieboldianus/TagMaps/commit/866314bc5c8132512e1448269c236124e66e12ec))

* refactor: improve encapsulation, remove obsolete comments ([`305c8a5`](https://github.com/Sieboldianus/TagMaps/commit/305c8a5972576122b418aea26f90af13706f2d2c))

* refactor(cluster): improve encapsulation of getting alpha shapes ([`1f7cf6b`](https://github.com/Sieboldianus/TagMaps/commit/1f7cf6bda6a7bae50ba412e3f7db2b5fcbecb8b4))

* refactor: alpha shapes generation and and final output classes ([`0a8a44c`](https://github.com/Sieboldianus/TagMaps/commit/0a8a44c662697d32d70ef10b1d058772b2f37ff6))

* refactor: parametric handling of clusterers in main ([`cd2b4b4`](https://github.com/Sieboldianus/TagMaps/commit/cd2b4b4dd2960778fc646785a7afd7371c195b85))

* refactor: pack interface buttons in separate methods ([`8f544cd`](https://github.com/Sieboldianus/TagMaps/commit/8f544cd3f360f9323bb9ffde5a222cd32e04afb6))

* refactor: use class constant for defining clusterer type ([`4bcca7a`](https://github.com/Sieboldianus/TagMaps/commit/4bcca7a346002e8a0d6c9b8e0cb371a8cccd2a42))

* refactor: cleanup interface listbox selection ([`8f2437e`](https://github.com/Sieboldianus/TagMaps/commit/8f2437e02a18ec3f851e32cc4c654804b0f9f919))

* refactor: emoji and tags handled separately ([`4f89a0f`](https://github.com/Sieboldianus/TagMaps/commit/4f89a0f0ff7bf0c32e559181e41b0495a5096720))

* refactor: load_data refactor tested, tkinter works ([`bc295e2`](https://github.com/Sieboldianus/TagMaps/commit/bc295e2fbc249fc51debeb22434a7758d0e61413))

* refactor: use namedtuple for essential structure

- intead of extra class ([`b2a7fb0`](https://github.com/Sieboldianus/TagMaps/commit/b2a7fb0ceaf65110657a6ce6f88abe67601e9c88))

* refactor: add separate files for cluster and interace ([`e3ea47d`](https://github.com/Sieboldianus/TagMaps/commit/e3ea47db01b362ffea39d517080182a97d0836ff))

* refactor: factored LoadData to separate class

- remeaining: use namedtuple instead of
separate class structure (current result: tkinter error) ([`33c076a`](https://github.com/Sieboldianus/TagMaps/commit/33c076a97b70af1bf1730a714aed70579d5059c6))

* refactor: update cx_freeze version var ([`83da437`](https://github.com/Sieboldianus/TagMaps/commit/83da4373fc4ed7a0af75c98361191f12ffbe6ff0))

* refactor(load_data): first part of load data structure ([`8f603da`](https://github.com/Sieboldianus/TagMaps/commit/8f603da85f8d729b7f48c91a9535ddb3b3a1d69e))

* refactor: remove sourcemapping_lbsn.ini ([`900dbe7`](https://github.com/Sieboldianus/TagMaps/commit/900dbe7551dcfc67162c59db685bd342332b8b60))

### Style

* style: cleaned imports, fixed, emoji name replacement ([`134f2f2`](https://github.com/Sieboldianus/TagMaps/commit/134f2f2a573a5b7f088709b02ff1b2ad44a84bb1))

* style: cleaned code, removed obsolete imports ([`6d4ad7c`](https://github.com/Sieboldianus/TagMaps/commit/6d4ad7c70bede5578616752edf0898deac8e808c))

* style:  use attr instead of custom class for shared structures ([`de552b3`](https://github.com/Sieboldianus/TagMaps/commit/de552b39b3e1fb19730323f4a207bc21b960b80d))

* style: more consistent metrics reporting, added abbreviation

- todo: explain abbreviations in docs ([`73ecb9a`](https://github.com/Sieboldianus/TagMaps/commit/73ecb9ac42dbe6cf35d20504f45ff3927455b853))

* style: move cluster type to shared structure ([`c169d23`](https://github.com/Sieboldianus/TagMaps/commit/c169d23b2dee764dadc62445085c5b5f164f6bac))

* style: improved reporting of statistics ([`34c955e`](https://github.com/Sieboldianus/TagMaps/commit/34c955ef39dd5207b790afe733d8b7cb76f7bf72))

* style: use better emoji font in plt output

- refactor of suptitle generation ([`c05663f`](https://github.com/Sieboldianus/TagMaps/commit/c05663f205069a4d1c0064563a4837a7aebf9c33))

* style: reporting emax and tmax ([`453e23a`](https://github.com/Sieboldianus/TagMaps/commit/453e23af2fec382f4c05e8c34b31d65b3b2fa34a))

### Unknown

* add test py for emoji handling ([`10c65ad`](https://github.com/Sieboldianus/TagMaps/commit/10c65ad77985316fd9b9bf0d6c75c770e58bd16c))

* (Apparently) fixed bug with location removal ([`2e9d3d2`](https://github.com/Sieboldianus/TagMaps/commit/2e9d3d2322fef239e29214cb8b4215fc9495d743))

* fix emoji csv output missing ([`2dd4acb`](https://github.com/Sieboldianus/TagMaps/commit/2dd4acbf8c5c991ea9caf53680605e3965613683))

* fixed bug with sorting final output shape ([`093d496`](https://github.com/Sieboldianus/TagMaps/commit/093d4964d3c632d62e81121b702328a1be965713))

* test refactor working, remaining issue with sort ([`250a290`](https://github.com/Sieboldianus/TagMaps/commit/250a29013ca7fc44e88ec3985d302b0127f69171))

* normalization for centroids and itemized clusters, location clutering ([`60970b6`](https://github.com/Sieboldianus/TagMaps/commit/60970b6c8ae86ed24e6d1549f085348c82985e20))

* refactored output into smaller methods ([`9dcf22e`](https://github.com/Sieboldianus/TagMaps/commit/9dcf22ed3db196c5b4218958820692ba87ef36bd))

* refactor of overall clustering and output module

- still some bugs ([`8561dcc`](https://github.com/Sieboldianus/TagMaps/commit/8561dcc86e55d1866e35578334e812f104752691))

* default cluster distance adapt to LOCATIONS ([`087f0c9`](https://github.com/Sieboldianus/TagMaps/commit/087f0c9f8e8f66ff4da059e7dfd83f63858b87c3))

* refactor initial alpha shapes part, not tested ([`ea66395`](https://github.com/Sieboldianus/TagMaps/commit/ea66395945418cd688cfe1279f38ad0d67e9d764))

* fix for clipping location list (allow all) ([`6580e3d`](https://github.com/Sieboldianus/TagMaps/commit/6580e3de60d3f6eb30eaddda8eb03039d0bd2eb6))

* add better handling of long tail removal for emoji and tag counters ([`5cb575f`](https://github.com/Sieboldianus/TagMaps/commit/5cb575fce1166ee631ad8eb3df3733dcc004afd9))

* intermediate refactor: cluster preview and map preview works

TODO: process_data refactor ([`e015f54`](https://github.com/Sieboldianus/TagMaps/commit/e015f543386247977d9ce248dde82e40bf643f05))

* refactor - cluster preview works ([`115576e`](https://github.com/Sieboldianus/TagMaps/commit/115576e41e5b61824e2126c4f14df74a78f546b8))

* refactor - selection of posts works

issues: no preview map ([`0b1386c`](https://github.com/Sieboldianus/TagMaps/commit/0b1386c5c8b399ef4a3e3cd5e9aff379d62ddeb6))

* fixed type bug for dict, interface starts ([`f4c85c5`](https://github.com/Sieboldianus/TagMaps/commit/f4c85c531ae1e4e5c7bc72266a1cdeb0d8f24955))

* first stage interface cluster refactor, not tested ([`7aa1f1b`](https://github.com/Sieboldianus/TagMaps/commit/7aa1f1b25a93cf51981d16c5358d6cc630a83d58))

* first stage interface cluster refactor, not tested ([`f594dbb`](https://github.com/Sieboldianus/TagMaps/commit/f594dbb74874939c4662530d117319d1b558735a))

* minor broken class fix ([`b315f6f`](https://github.com/Sieboldianus/TagMaps/commit/b315f6fe4929e7da86525a2ed04a4e22ccf7aadc))

* refactor - started separating cluster and interface methods ([`ac849d4`](https://github.com/Sieboldianus/TagMaps/commit/ac849d43e4f884c45e3647e579ee29c07d56ea0f))

* - initial refactor of interface and cluster module ([`3c672b6`](https://github.com/Sieboldianus/TagMaps/commit/3c672b6b0c59e27ec0f98ffe0cc45cf1b06572c3))

* intermediate refactoring: tests working after
moving code to load_data.py ([`cc3af53`](https://github.com/Sieboldianus/TagMaps/commit/cc3af53c3190739484a3bcd6bd9f1ffd8000eab3))

* replace CleanedPost class structure with named tuple ([`7cbd4d4`](https://github.com/Sieboldianus/TagMaps/commit/7cbd4d4fde56217d1a0243563010f8cc4a12bf1d))

* remove jProcessing since it is still Alpha and has import problems ([`1a2414d`](https://github.com/Sieboldianus/TagMaps/commit/1a2414dcfc7d68a8424742761f8657da62ffb377))

* exclude lbsntransform: no longer needed ([`b1f6529`](https://github.com/Sieboldianus/TagMaps/commit/b1f6529c3cbb587e791fa078ef272649cfc4c6b4))

* refactor part - load data ([`4a26059`](https://github.com/Sieboldianus/TagMaps/commit/4a26059beee8a4be31a1cd14ed3bf68924eb94f5))

* refactor (config): implement class for storing mapping args ([`e4f9f15`](https://github.com/Sieboldianus/TagMaps/commit/e4f9f157d3f09466a587221899adc8cac8d13d9e))

* fix (config): rename sourcemapping file ([`75b97d0`](https://github.com/Sieboldianus/TagMaps/commit/75b97d0c97aca30cd6e1c61097e841687ba9109a))


## v0.10.4 (2019-01-04)

### Fix

* fix: remote repo ref publish ([`dbfe1ba`](https://github.com/Sieboldianus/TagMaps/commit/dbfe1ba13f138e6b02c2f4187e14a7b73ef242c3))


## v0.10.3 (2019-01-04)

### Fix

* fix: remote publish ([`c04cd16`](https://github.com/Sieboldianus/TagMaps/commit/c04cd16193eeda800f918e20454382f2cb17f9a0))


## v0.10.2 (2019-01-04)

### Fix

* fix: fix auto versioning

- disbale pypi auto upload ([`2884b48`](https://github.com/Sieboldianus/TagMaps/commit/2884b481416e04436ffbca46f58f284cad3f4424))


## v0.10.1 (2019-01-04)

### Chore

* chore: disabled pypi upload ([`1bab372`](https://github.com/Sieboldianus/TagMaps/commit/1bab3728dc9501600ba25692eef6762b6138b961))

* chore: disabled auto pypi upload ([`d340402`](https://github.com/Sieboldianus/TagMaps/commit/d3404022b41438506d5b19566c656fb48492d933))

### Unknown

* Merge branch &#39;master&#39; of gitlab.vgiscience.de:ad/TagCluster ([`e4b2f0d`](https://github.com/Sieboldianus/TagMaps/commit/e4b2f0daedc90b7c0429db3ec413f4ead5d7eab2))

* Merge branch &#39;dev&#39; ([`7340bbb`](https://github.com/Sieboldianus/TagMaps/commit/7340bbbbade20ee56f0cfc646c48f0a5e79c1a4f))


## v0.10.0 (2019-01-04)

### Unknown

* chore (git): added vscode to gitignore ([`f6f14c9`](https://github.com/Sieboldianus/TagMaps/commit/f6f14c93c5c45a2bd98a979f1e65d93e2b746e05))

* docs (config): added  help msgs to all input args ([`f082fc3`](https://github.com/Sieboldianus/TagMaps/commit/f082fc3aee605fee556817ad207af39f434eab54))


## v0.9.40 (2019-01-04)

### Chore

* chore: added semantic versioning ([`1e81d7e`](https://github.com/Sieboldianus/TagMaps/commit/1e81d7e9ff71614f04d8a920ac49784cf0c9453a))

### Style

* style: changed CRLF to LF in all files

- Minor style changes in config.py ([`dec9c3e`](https://github.com/Sieboldianus/TagMaps/commit/dec9c3ee60a77ad83b08c20323c06699261c4edb))

### Unknown

* Removed obsolete pptx tutorials ([`65d1845`](https://github.com/Sieboldianus/TagMaps/commit/65d18457469d28f012f7283054a89379896a6ef9))

* Initial Load Data Class
- currently, not working ([`554c804`](https://github.com/Sieboldianus/TagMaps/commit/554c8044050b4b181f920d8958725a680bf1e266))

* Initial work on load_data class ([`d2804aa`](https://github.com/Sieboldianus/TagMaps/commit/d2804aa9d6f3419e1959823495853ab17a2a44e4))

* Added License File. ([`9f42893`](https://github.com/Sieboldianus/TagMaps/commit/9f428935db12277a425c4161aac42268d1e7c7b9))

* Small refactoring: config and logging moved to Utils (class) ([`db642b7`](https://github.com/Sieboldianus/TagMaps/commit/db642b78e18a9a72789a2c61aff7e1b6f490527a))

* Code style improvements ([`b1da3eb`](https://github.com/Sieboldianus/TagMaps/commit/b1da3eb3786f0337ec66ac9f0f665dcd1e81329a))

* Several implementation &amp; installation updates
- Removed tkinter from setup.py, since it is installed by default
- updated cx_setup
- corrected cx_setup readme ([`7f92747`](https://github.com/Sieboldianus/TagMaps/commit/7f927470b3f2c0c8e3ad37d411fd9cdc1c036f49))

* Minor style improvements ([`03480c0`](https://github.com/Sieboldianus/TagMaps/commit/03480c00fcdd30b7fe3d65eb0dadda8a900caf07))

* Added Main Logging Handler ([`e0bec8b`](https://github.com/Sieboldianus/TagMaps/commit/e0bec8b4883dd1384861d8f34301fd7706470357))

* refactored input args to config.py ([`75f0530`](https://github.com/Sieboldianus/TagMaps/commit/75f0530f34a097e416bb47c3caebad29096ce0a2))

* Added Version File, Manifest.in; updated setup.py ([`cd31090`](https://github.com/Sieboldianus/TagMaps/commit/cd31090f22e5f34f2ab5b62d6c120174e7aca7cd))

* Added Total Tag Count Stat after Long Tail removal ([`8cac3a8`](https://github.com/Sieboldianus/TagMaps/commit/8cac3a8648ed2590982b50679a42c9fd2ad0bc0f))

* Updated fromLBSN_old input ([`0dc1770`](https://github.com/Sieboldianus/TagMaps/commit/0dc1770d6a6ff3f5c85cae44910370904a2c7cee))

* Minor fix for auto cluster cutting dist ref ([`78b8824`](https://github.com/Sieboldianus/TagMaps/commit/78b8824ddf3c2f3834f27ed3e6fbb7a69a44cf9e))

* Moved test directory inside code folder ([`7f047d5`](https://github.com/Sieboldianus/TagMaps/commit/7f047d5d5fb55b49ea00174ea92729c8f5251bee))

* Added test layout for pytest ([`3ecf1f3`](https://github.com/Sieboldianus/TagMaps/commit/3ecf1f34e0442ba7d2141dc261b130d4a4147369))

* Minor formatting fixes/removed debug output
- added correct path to checkEmojiType ([`d16c6c6`](https://github.com/Sieboldianus/TagMaps/commit/d16c6c6f9dd767037a21873b9583ba34adf8856d))

* Fixed multiple character emoji tcl exception handling ([`fc149f8`](https://github.com/Sieboldianus/TagMaps/commit/fc149f8e71eecdf87f5eacebf154101c03ffcfa0))

* Added correct Script access ([`1ced92c`](https://github.com/Sieboldianus/TagMaps/commit/1ced92ca2cd083df57bddfe262798b17883c0055))

* Small refactoring (file rename, moves)
- moved input and config out of package folder, updated cx_freeze
- added input arg for bottom user count limit
- some small bugfixes on compilation
- updated default cmds ([`da8b927`](https://github.com/Sieboldianus/TagMaps/commit/da8b92791fa3440ef4fcf92efff7c96262ef0f75))

* Added img refs ([`1c10b00`](https://github.com/Sieboldianus/TagMaps/commit/1c10b0031035d502549017da7733404385481be9))

* Hotfix to enable build using cx_freeze
- this is a small refactor so that tagmaps can still be run with new 5.01 cx_freeze
- created package, installable with setuptools (e.g. dev mode)
- separated cx_freeze setup
- renamed generateTagClusters.py to __main__.py and added entrypoint accordingly for direct command line execution
- moved utils to subfolder (classes), renamed references
- moved main code to &#39;def main():&#39;, also added a number of globals where it was unavoidable with current setup
- successfully tested build ([`664939b`](https://github.com/Sieboldianus/TagMaps/commit/664939b1445f90ce489a83c82bf1410a9367e2fd))

* Revert &#34;Added Fixes for .utils import; did not work&#34;

This reverts commit 9aa603ec5310b057ca8da818b8cdc6b9eabe3e23. ([`921a68d`](https://github.com/Sieboldianus/TagMaps/commit/921a68d77c9ca7a380d48093e1ad4627d96338c1))

* Added Fixes for .utils import; did not work ([`9aa603e`](https://github.com/Sieboldianus/TagMaps/commit/9aa603ec5310b057ca8da818b8cdc6b9eabe3e23))

* Renamed def_functions to utils.py ([`30f67c2`](https://github.com/Sieboldianus/TagMaps/commit/30f67c2b421abeaeb1a5fe79b43bad3390ac717e))

* Begin refactoring ([`6c76a05`](https://github.com/Sieboldianus/TagMaps/commit/6c76a05c209ed6b46b25546d869046063436ab1f))

* Minor refactoring and improvement of stats output; added new args ([`8ba9b85`](https://github.com/Sieboldianus/TagMaps/commit/8ba9b8541af25933e3fed5b40506470a4dc33995))

* Updated paths in setup.py to new structure ([`23e3e2e`](https://github.com/Sieboldianus/TagMaps/commit/23e3e2ecfcdbda78bcb6801c7ca6631befa927d7))

* Moved Files to Subdir ([`95917b7`](https://github.com/Sieboldianus/TagMaps/commit/95917b71c3362eaa25ef8eb16250804d635599a9))

* Prepared to move files ([`d74d858`](https://github.com/Sieboldianus/TagMaps/commit/d74d858c9b4c38617fa56ce9910343f1f458a1f4))

* Fixed minor issue in statistics ([`1730889`](https://github.com/Sieboldianus/TagMaps/commit/17308891b5aeceabb89efc84096eaf5fe4f9a47c))

* Added Function/Files to manually override place lat/lng or filter out specific places ([`c1edef3`](https://github.com/Sieboldianus/TagMaps/commit/c1edef31878b74ed104f6918f3b3f36d799a6690))

* Added arg for ShapefileIntersect ([`23a8e66`](https://github.com/Sieboldianus/TagMaps/commit/23a8e6620c0d8d47633c6c1f12182e790e9a910a))

* Added Shapefile Intersect ([`cba2ab2`](https://github.com/Sieboldianus/TagMaps/commit/cba2ab2f8beac5dec08f684d39cbdf3dfc20e04d))

* Bugfixes; Tested Version (Virginia) ([`aaa025a`](https://github.com/Sieboldianus/TagMaps/commit/aaa025a7142584fece6e8394de0b3171f7fc74d3))

* All Defaults Set Correctly ([`4a29e9c`](https://github.com/Sieboldianus/TagMaps/commit/4a29e9c0aac2a7cf8f5751d234a9e716d706312e))

* Updated code to new lbsn csv structure; Fixed some bugs with emoji clustering ([`e9142ac`](https://github.com/Sieboldianus/TagMaps/commit/e9142acf3756bd6762fc2e5b584107591421df00))

* Updated all messages to f-strings formatting ([`6015276`](https://github.com/Sieboldianus/TagMaps/commit/6015276ab8e1f0bac676a1b036adfa1642dbf910))

* Topic Modeling ([`e2b1bc8`](https://github.com/Sieboldianus/TagMaps/commit/e2b1bc85271b86c3447a0893722b8ebcd99c8e8d))

* Added additional start arguments; started conversion of output formatting to f-strings ([`05cedf2`](https://github.com/Sieboldianus/TagMaps/commit/05cedf26edeefe6e69a8419726f24687d4907b64))

* Added Topic Modeling Output CSV ([`4f628bf`](https://github.com/Sieboldianus/TagMaps/commit/4f628bfb312ccdb3e7d28a7d1e79b3170201670f))

* Refactoring, better implementation of emoji code (TU Campus tested) ([`5e62c7c`](https://github.com/Sieboldianus/TagMaps/commit/5e62c7c463d33a2e876b64356dd79dd7d69e0b39))

* Minor refactoring and code optimization ([`7a4572e`](https://github.com/Sieboldianus/TagMaps/commit/7a4572e8a4ad1f05281eca126a488eb5c6b83723))

* Minor debug ([`e044d20`](https://github.com/Sieboldianus/TagMaps/commit/e044d209f1420b4388f56284591db4f4b8984513))

* Included and tested LocalSaturation Check; additional start parameters ([`7bf3637`](https://github.com/Sieboldianus/TagMaps/commit/7bf36377f0b3f96044a070202bfc2df47ee1d8b7))

* Added tag saturation code: filters tags with no local clusters/patterns ([`979596a`](https://github.com/Sieboldianus/TagMaps/commit/979596a2c92298040af9edfa4de7bc6fe904b6d3))

* Added custom argument for EPSG (crs projection code)

- buggy because of different projection distances
- some crs require modification to the transformation function ([`47216a8`](https://github.com/Sieboldianus/TagMaps/commit/47216a83faddb33053eba5bcb758e24b7d5996d8))

* Revised Alpha Shape generation: now working on local to regional to continental scales ([`42f0435`](https://github.com/Sieboldianus/TagMaps/commit/42f04354e2e1be0575df46cd17e55cb364c559f3))

* Minor fix for Math Value Error on Alpha Shapes ([`9361e68`](https://github.com/Sieboldianus/TagMaps/commit/9361e68a00898912bc100e882e112b2b0de9b632))

* Added projection to suitable UTM coordinate system before Alpha Shapes

- moved up from version 0.9.1 to 0.9.2
- optimization of Alpha Shapes tested for local and city scales (Copenhagen, Berlin Spreeinsel, Highpark) ([`0965156`](https://github.com/Sieboldianus/TagMaps/commit/0965156688175b5ea9e434ec6502c8e3bc0284c6))

* Included output shapefile projection to correct UTM Zone ([`efb6e80`](https://github.com/Sieboldianus/TagMaps/commit/efb6e80efdcfb0d7ddf06d635d1c0de47f9f2af8))

* Fixed serious issue that would result in wrong order of HImPs assigned to results ([`992cb17`](https://github.com/Sieboldianus/TagMaps/commit/992cb17fe94a5e3a4ee6915ce1d015d3b86353d9))

* Added functionality to process CSV data from Inf Würzburg Sensor data ([`84352e9`](https://github.com/Sieboldianus/TagMaps/commit/84352e9e4f89d8b709f5b13aa45955ec1cd859e8))

* Added InstagramEmji cmd ([`2cbdc01`](https://github.com/Sieboldianus/TagMaps/commit/2cbdc0142a0ba39419b085da92b630afcd0da622))

* Updated for accurate Emoji handling (without Fitzpatrick modifiers) ([`c67f464`](https://github.com/Sieboldianus/TagMaps/commit/c67f464770b0a392bbd8f243da5b99768719f421))

* Remove ignored files ([`e6ccfb5`](https://github.com/Sieboldianus/TagMaps/commit/e6ccfb51c68110878a074f3557f2e5964ccfecc4))

* Updated gitignore ([`2b7ab3a`](https://github.com/Sieboldianus/TagMaps/commit/2b7ab3adba4b379cd745afd7e9a05dc731222d57))

* Updated gitignore ([`5001d5b`](https://github.com/Sieboldianus/TagMaps/commit/5001d5b9406540357a92c40121a6c5834073d28e))

* Minor bugfix for geometry error in Alpha Shapes ([`ff38679`](https://github.com/Sieboldianus/TagMaps/commit/ff38679f76343cd47b8a356e144ef3dbb40cc2c8))

* cx_Freeze self executable integration. Minor GUI updates &amp; HCI improvements ([`aeb7120`](https://github.com/Sieboldianus/TagMaps/commit/aeb7120daf820cca0fcf7e4b84fff7d0fe85fcfa))

* Added additional outputs, minor summarizing fixes, added Photo Location Cluster

- successfully tested! ([`8ef77f5`](https://github.com/Sieboldianus/TagMaps/commit/8ef77f5666dbb129815463a50f5cd4d95de4c844))

* Final data output, tested! ([`611bef5`](https://github.com/Sieboldianus/TagMaps/commit/611bef5bf1fdd41a35e4030f8a73b34c164ff084))

* Writing to Shapefile works! ([`3d5f6ef`](https://github.com/Sieboldianus/TagMaps/commit/3d5f6ef3191a4965ba7cacd09548cc72627d3207))

* Added Alpha Shapes function ([`03447a4`](https://github.com/Sieboldianus/TagMaps/commit/03447a4cbc374e0e9d599c1c40445bd2dc5e1ddc))

* Various fixes ([`8e1de11`](https://github.com/Sieboldianus/TagMaps/commit/8e1de11f413460d5d20e155ccfe815cd0decc330))

* Added multithreaded execution of HDBSCAN cluster.fit() ([`ddaa6b9`](https://github.com/Sieboldianus/TagMaps/commit/ddaa6b921fc63b1a3bcecd1af9316cd51f7a2445))

* Minor formatting changes ([`4335bed`](https://github.com/Sieboldianus/TagMaps/commit/4335bed55c52d0fc38b4438dac254948b90c8652))

* Final working version before Christmas ([`1e2f251`](https://github.com/Sieboldianus/TagMaps/commit/1e2f251897a81fdec7adf3eb99706114c6a217c3))

* Implemented multi-view matplotlib cluster interface; Fixed some bugs ([`31acf86`](https://github.com/Sieboldianus/TagMaps/commit/31acf869b4cd53f2230a6d979a3583dc8c0ddba0))

* Floating command line windows tkinter version works

- design issues remain ([`3c295f4`](https://github.com/Sieboldianus/TagMaps/commit/3c295f40f7953f67945f8fd6a203471284461426))

* HDBCLUSTER IMPLEMENT ([`a569fe6`](https://github.com/Sieboldianus/TagMaps/commit/a569fe6cb1adb41e9fe8cb80e8a67573fa118c85))

* Added namedtuple for output structure, added numeric-tag-exclusion ([`db37071`](https://github.com/Sieboldianus/TagMaps/commit/db37071000042566d6ee05d5bae66867c0e0ed13))

* Initial Commit ([`03732ce`](https://github.com/Sieboldianus/TagMaps/commit/03732ce672254e10ee19f5dd4723d297d75037b4))
