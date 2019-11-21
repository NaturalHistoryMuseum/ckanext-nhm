(window["webpackJsonpsearch"] = window["webpackJsonpsearch"] || []).push([[2],{

/***/ "./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader/lib/index.js?!./src/components/ResourceList.vue?vue&type=script&lang=js&":
/*!****************************************************************************************************************************************************!*\
  !*** ./node_modules/babel-loader/lib!./node_modules/vue-loader/lib??vue-loader-options!./src/components/ResourceList.vue?vue&type=script&lang=js& ***!
  \****************************************************************************************************************************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var vuex__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! vuex */ \"./node_modules/vuex/dist/vuex.esm.js\");\nfunction ownKeys(object, enumerableOnly) { var keys = Object.keys(object); if (Object.getOwnPropertySymbols) { var symbols = Object.getOwnPropertySymbols(object); if (enumerableOnly) symbols = symbols.filter(function (sym) { return Object.getOwnPropertyDescriptor(object, sym).enumerable; }); keys.push.apply(keys, symbols); } return keys; }\n\nfunction _objectSpread(target) { for (var i = 1; i < arguments.length; i++) { var source = arguments[i] != null ? arguments[i] : {}; if (i % 2) { ownKeys(source, true).forEach(function (key) { _defineProperty(target, key, source[key]); }); } else if (Object.getOwnPropertyDescriptors) { Object.defineProperties(target, Object.getOwnPropertyDescriptors(source)); } else { ownKeys(source).forEach(function (key) { Object.defineProperty(target, key, Object.getOwnPropertyDescriptor(source, key)); }); } } return target; }\n\nfunction _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }\n\n//\n//\n//\n//\n//\n//\n//\n//\n//\n//\n//\n//\n//\n//\n//\n//\n//\n//\n//\n//\n//\n\n/* harmony default export */ __webpack_exports__[\"default\"] = ({\n  name: 'ResourceList',\n  data: function data() {\n    return {\n      allResourcesToggle: false\n    };\n  },\n  computed: _objectSpread({}, Object(vuex__WEBPACK_IMPORTED_MODULE_0__[\"mapState\"])(['resourceIds']), {}, Object(vuex__WEBPACK_IMPORTED_MODULE_0__[\"mapState\"])('constants', ['packageList']), {\n    resourceIds: {\n      get: function get() {\n        return this.$store.state.resourceIds;\n      },\n      set: function set(value) {\n        this.$store.commit('setResourceIds', value);\n      }\n    }\n  }),\n  methods: _objectSpread({}, Object(vuex__WEBPACK_IMPORTED_MODULE_0__[\"mapMutations\"])(['togglePackageResources']), {\n    toggleAllResourceSelect: function toggleAllResourceSelect(event) {\n      if (event.target.checked) {\n        this.$store.commit('selectAllResources');\n      } else {\n        this.resourceIds = [];\n      }\n    }\n  }),\n  watch: {\n    resourceIds: function resourceIds(_resourceIds, oldResourceIds) {\n      if (_resourceIds.length < oldResourceIds.length) {\n        this.allResourcesToggle = false;\n      }\n    }\n  }\n});\n\n//# sourceURL=webpack://search/./src/components/ResourceList.vue?./node_modules/babel-loader/lib!./node_modules/vue-loader/lib??vue-loader-options");

/***/ }),

/***/ "./node_modules/vue-loader/lib/loaders/templateLoader.js?!./node_modules/vue-loader/lib/index.js?!./src/components/ResourceList.vue?vue&type=template&id=3d24fffc&":
/*!******************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/vue-loader/lib/loaders/templateLoader.js??vue-loader-options!./node_modules/vue-loader/lib??vue-loader-options!./src/components/ResourceList.vue?vue&type=template&id=3d24fffc& ***!
  \******************************************************************************************************************************************************************************************************/
/*! exports provided: render, staticRenderFns */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, \"render\", function() { return render; });\n/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, \"staticRenderFns\", function() { return staticRenderFns; });\nvar render = function() {\n  var _vm = this\n  var _h = _vm.$createElement\n  var _c = _vm._self._c || _h\n  return _c(\n    \"div\",\n    {\n      staticClass:\n        \"fields resourceid-list floating flex-container flex-column flex-left\"\n    },\n    [\n      _c(\"div\", [\n        _c(\"input\", {\n          directives: [\n            {\n              name: \"model\",\n              rawName: \"v-model\",\n              value: _vm.allResourcesToggle,\n              expression: \"allResourcesToggle\"\n            }\n          ],\n          attrs: { type: \"checkbox\", id: \"toggleAll\" },\n          domProps: {\n            checked: Array.isArray(_vm.allResourcesToggle)\n              ? _vm._i(_vm.allResourcesToggle, null) > -1\n              : _vm.allResourcesToggle\n          },\n          on: {\n            change: [\n              function($event) {\n                var $$a = _vm.allResourcesToggle,\n                  $$el = $event.target,\n                  $$c = $$el.checked ? true : false\n                if (Array.isArray($$a)) {\n                  var $$v = null,\n                    $$i = _vm._i($$a, $$v)\n                  if ($$el.checked) {\n                    $$i < 0 && (_vm.allResourcesToggle = $$a.concat([$$v]))\n                  } else {\n                    $$i > -1 &&\n                      (_vm.allResourcesToggle = $$a\n                        .slice(0, $$i)\n                        .concat($$a.slice($$i + 1)))\n                  }\n                } else {\n                  _vm.allResourcesToggle = $$c\n                }\n              },\n              _vm.toggleAllResourceSelect\n            ]\n          }\n        }),\n        _vm._v(\" \"),\n        _c(\"label\", { attrs: { for: \"toggleAll\" } }, [_vm._v(\"Select all\")])\n      ]),\n      _vm._v(\" \"),\n      _vm._l(_vm.packageList, function(pkg, index) {\n        return _c(\"span\", { key: pkg.id }, [\n          _c(\n            \"a\",\n            {\n              attrs: { href: \"#\", id: pkg.id, value: pkg.id },\n              on: {\n                click: function($event) {\n                  return _vm.togglePackageResources(index)\n                }\n              }\n            },\n            [_vm._v(_vm._s(pkg.name))]\n          ),\n          _vm._v(\" \"),\n          _c(\n            \"div\",\n            { staticClass: \"fields\" },\n            _vm._l(pkg.resources, function(resource) {\n              return _c(\"span\", { key: resource.id }, [\n                _c(\"input\", {\n                  directives: [\n                    {\n                      name: \"model\",\n                      rawName: \"v-model\",\n                      value: _vm.resourceIds,\n                      expression: \"resourceIds\"\n                    }\n                  ],\n                  attrs: { type: \"checkbox\", id: resource.id },\n                  domProps: {\n                    value: resource.id,\n                    checked: Array.isArray(_vm.resourceIds)\n                      ? _vm._i(_vm.resourceIds, resource.id) > -1\n                      : _vm.resourceIds\n                  },\n                  on: {\n                    change: function($event) {\n                      var $$a = _vm.resourceIds,\n                        $$el = $event.target,\n                        $$c = $$el.checked ? true : false\n                      if (Array.isArray($$a)) {\n                        var $$v = resource.id,\n                          $$i = _vm._i($$a, $$v)\n                        if ($$el.checked) {\n                          $$i < 0 && (_vm.resourceIds = $$a.concat([$$v]))\n                        } else {\n                          $$i > -1 &&\n                            (_vm.resourceIds = $$a\n                              .slice(0, $$i)\n                              .concat($$a.slice($$i + 1)))\n                        }\n                      } else {\n                        _vm.resourceIds = $$c\n                      }\n                    }\n                  }\n                }),\n                _vm._v(\" \"),\n                _c(\"label\", { attrs: { for: resource.id } }, [\n                  _vm._v(_vm._s(resource.name))\n                ])\n              ])\n            }),\n            0\n          )\n        ])\n      })\n    ],\n    2\n  )\n}\nvar staticRenderFns = []\nrender._withStripped = true\n\n\n\n//# sourceURL=webpack://search/./src/components/ResourceList.vue?./node_modules/vue-loader/lib/loaders/templateLoader.js??vue-loader-options!./node_modules/vue-loader/lib??vue-loader-options");

/***/ }),

/***/ "./src/components/ResourceList.vue":
/*!*****************************************!*\
  !*** ./src/components/ResourceList.vue ***!
  \*****************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _ResourceList_vue_vue_type_template_id_3d24fffc___WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./ResourceList.vue?vue&type=template&id=3d24fffc& */ \"./src/components/ResourceList.vue?vue&type=template&id=3d24fffc&\");\n/* harmony import */ var _ResourceList_vue_vue_type_script_lang_js___WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./ResourceList.vue?vue&type=script&lang=js& */ \"./src/components/ResourceList.vue?vue&type=script&lang=js&\");\n/* empty/unused harmony star reexport *//* harmony import */ var _node_modules_vue_loader_lib_runtime_componentNormalizer_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../../node_modules/vue-loader/lib/runtime/componentNormalizer.js */ \"./node_modules/vue-loader/lib/runtime/componentNormalizer.js\");\n\n\n\n\n\n/* normalize component */\n\nvar component = Object(_node_modules_vue_loader_lib_runtime_componentNormalizer_js__WEBPACK_IMPORTED_MODULE_2__[\"default\"])(\n  _ResourceList_vue_vue_type_script_lang_js___WEBPACK_IMPORTED_MODULE_1__[\"default\"],\n  _ResourceList_vue_vue_type_template_id_3d24fffc___WEBPACK_IMPORTED_MODULE_0__[\"render\"],\n  _ResourceList_vue_vue_type_template_id_3d24fffc___WEBPACK_IMPORTED_MODULE_0__[\"staticRenderFns\"],\n  false,\n  null,\n  null,\n  null\n  \n)\n\n/* hot reload */\nif (false) { var api; }\ncomponent.options.__file = \"src/components/ResourceList.vue\"\n/* harmony default export */ __webpack_exports__[\"default\"] = (component.exports);\n\n//# sourceURL=webpack://search/./src/components/ResourceList.vue?");

/***/ }),

/***/ "./src/components/ResourceList.vue?vue&type=script&lang=js&":
/*!******************************************************************!*\
  !*** ./src/components/ResourceList.vue?vue&type=script&lang=js& ***!
  \******************************************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _node_modules_babel_loader_lib_index_js_node_modules_vue_loader_lib_index_js_vue_loader_options_ResourceList_vue_vue_type_script_lang_js___WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../node_modules/babel-loader/lib!../../node_modules/vue-loader/lib??vue-loader-options!./ResourceList.vue?vue&type=script&lang=js& */ \"./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader/lib/index.js?!./src/components/ResourceList.vue?vue&type=script&lang=js&\");\n/* empty/unused harmony star reexport */ /* harmony default export */ __webpack_exports__[\"default\"] = (_node_modules_babel_loader_lib_index_js_node_modules_vue_loader_lib_index_js_vue_loader_options_ResourceList_vue_vue_type_script_lang_js___WEBPACK_IMPORTED_MODULE_0__[\"default\"]); \n\n//# sourceURL=webpack://search/./src/components/ResourceList.vue?");

/***/ }),

/***/ "./src/components/ResourceList.vue?vue&type=template&id=3d24fffc&":
/*!************************************************************************!*\
  !*** ./src/components/ResourceList.vue?vue&type=template&id=3d24fffc& ***!
  \************************************************************************/
/*! exports provided: render, staticRenderFns */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _node_modules_vue_loader_lib_loaders_templateLoader_js_vue_loader_options_node_modules_vue_loader_lib_index_js_vue_loader_options_ResourceList_vue_vue_type_template_id_3d24fffc___WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../node_modules/vue-loader/lib/loaders/templateLoader.js??vue-loader-options!../../node_modules/vue-loader/lib??vue-loader-options!./ResourceList.vue?vue&type=template&id=3d24fffc& */ \"./node_modules/vue-loader/lib/loaders/templateLoader.js?!./node_modules/vue-loader/lib/index.js?!./src/components/ResourceList.vue?vue&type=template&id=3d24fffc&\");\n/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, \"render\", function() { return _node_modules_vue_loader_lib_loaders_templateLoader_js_vue_loader_options_node_modules_vue_loader_lib_index_js_vue_loader_options_ResourceList_vue_vue_type_template_id_3d24fffc___WEBPACK_IMPORTED_MODULE_0__[\"render\"]; });\n\n/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, \"staticRenderFns\", function() { return _node_modules_vue_loader_lib_loaders_templateLoader_js_vue_loader_options_node_modules_vue_loader_lib_index_js_vue_loader_options_ResourceList_vue_vue_type_template_id_3d24fffc___WEBPACK_IMPORTED_MODULE_0__[\"staticRenderFns\"]; });\n\n\n\n//# sourceURL=webpack://search/./src/components/ResourceList.vue?");

/***/ })

}]);