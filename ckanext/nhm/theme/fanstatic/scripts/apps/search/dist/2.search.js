(window["webpackJsonpsearch"] = window["webpackJsonpsearch"] || []).push([[2],{

/***/ "./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader/lib/index.js?!./src/components/ResourceList.vue?vue&type=script&lang=js&":
/*!****************************************************************************************************************************************************!*\
  !*** ./node_modules/babel-loader/lib!./node_modules/vue-loader/lib??vue-loader-options!./src/components/ResourceList.vue?vue&type=script&lang=js& ***!
  \****************************************************************************************************************************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var vuex__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! vuex */ \"./node_modules/vuex/dist/vuex.esm.js\");\nfunction ownKeys(a,b){var c=Object.keys(a);if(Object.getOwnPropertySymbols){var d=Object.getOwnPropertySymbols(a);b&&(d=d.filter(function(b){return Object.getOwnPropertyDescriptor(a,b).enumerable})),c.push.apply(c,d)}return c}function _objectSpread(a){for(var b,c=1;c<arguments.length;c++)b=null==arguments[c]?{}:arguments[c],c%2?ownKeys(Object(b),!0).forEach(function(c){_defineProperty(a,c,b[c])}):Object.getOwnPropertyDescriptors?Object.defineProperties(a,Object.getOwnPropertyDescriptors(b)):ownKeys(Object(b)).forEach(function(c){Object.defineProperty(a,c,Object.getOwnPropertyDescriptor(b,c))});return a}function _defineProperty(a,b,c){return b in a?Object.defineProperty(a,b,{value:c,enumerable:!0,configurable:!0,writable:!0}):a[b]=c,a}//\n//\n//\n//\n//\n//\n//\n//\n//\n//\n//\n//\n//\n//\n//\n//\n//\n//\n//\n//\n//\n/* harmony default export */ __webpack_exports__[\"default\"] = ({name:\"ResourceList\",data:function data(){return{allResourcesToggle:!1}},computed:_objectSpread({},Object(vuex__WEBPACK_IMPORTED_MODULE_0__[\"mapState\"])(\"results/query/resources\",[\"packageList\"]),{},Object(vuex__WEBPACK_IMPORTED_MODULE_0__[\"mapGetters\"])(\"results/query/resources\",[\"packageResources\"]),{resourceIds:{get:function get(){return this.$store.state.results.query.resources.resourceIds},set:function set(a){this.setResourceIds(a)}}}),methods:_objectSpread({},Object(vuex__WEBPACK_IMPORTED_MODULE_0__[\"mapMutations\"])(\"results/query/resources\",[\"togglePackageResources\",\"selectAllResources\",\"setResourceIds\"]),{toggleAllResourceSelect:function toggleAllResourceSelect(a){a.target.checked?this.selectAllResources():this.resourceIds=[]},packageClick:function packageClick(a,b){b.preventDefault(),b.altKey?this.resourceIds=this.packageResources(a):this.togglePackageResources(a)}}),watch:{resourceIds:function resourceIds(a,b){a.length<b.length&&(this.allResourcesToggle=!1)}}});\n\n//# sourceURL=webpack://search/./src/components/ResourceList.vue?./node_modules/babel-loader/lib!./node_modules/vue-loader/lib??vue-loader-options");

/***/ }),

/***/ "./node_modules/vue-loader/lib/loaders/templateLoader.js?!./node_modules/vue-loader/lib/index.js?!./src/components/ResourceList.vue?vue&type=template&id=3d24fffc&":
/*!******************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/vue-loader/lib/loaders/templateLoader.js??vue-loader-options!./node_modules/vue-loader/lib??vue-loader-options!./src/components/ResourceList.vue?vue&type=template&id=3d24fffc& ***!
  \******************************************************************************************************************************************************************************************************/
/*! exports provided: render, staticRenderFns */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, \"render\", function() { return render; });\n/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, \"staticRenderFns\", function() { return staticRenderFns; });\nvar render = function() {\n  var _vm = this\n  var _h = _vm.$createElement\n  var _c = _vm._self._c || _h\n  return _c(\n    \"div\",\n    {\n      staticClass:\n        \"fields resourceid-list floating flex-container flex-column flex-left\"\n    },\n    [\n      _c(\"div\", [\n        _c(\"input\", {\n          directives: [\n            {\n              name: \"model\",\n              rawName: \"v-model\",\n              value: _vm.allResourcesToggle,\n              expression: \"allResourcesToggle\"\n            }\n          ],\n          attrs: { type: \"checkbox\", id: \"toggleAll\" },\n          domProps: {\n            checked: Array.isArray(_vm.allResourcesToggle)\n              ? _vm._i(_vm.allResourcesToggle, null) > -1\n              : _vm.allResourcesToggle\n          },\n          on: {\n            change: [\n              function($event) {\n                var $$a = _vm.allResourcesToggle,\n                  $$el = $event.target,\n                  $$c = $$el.checked ? true : false\n                if (Array.isArray($$a)) {\n                  var $$v = null,\n                    $$i = _vm._i($$a, $$v)\n                  if ($$el.checked) {\n                    $$i < 0 && (_vm.allResourcesToggle = $$a.concat([$$v]))\n                  } else {\n                    $$i > -1 &&\n                      (_vm.allResourcesToggle = $$a\n                        .slice(0, $$i)\n                        .concat($$a.slice($$i + 1)))\n                  }\n                } else {\n                  _vm.allResourcesToggle = $$c\n                }\n              },\n              _vm.toggleAllResourceSelect\n            ]\n          }\n        }),\n        _vm._v(\" \"),\n        _c(\"label\", { attrs: { for: \"toggleAll\" } }, [_vm._v(\"Select all\")])\n      ]),\n      _vm._v(\" \"),\n      _vm._l(_vm.packageList, function(pkg, index) {\n        return _c(\"span\", { key: pkg.id }, [\n          _c(\n            \"a\",\n            {\n              attrs: {\n                href: \"#\",\n                id: pkg.id,\n                value: pkg.id,\n                title: \"alt+click to select only this package\"\n              },\n              on: {\n                click: function($event) {\n                  return _vm.packageClick(index, $event)\n                }\n              }\n            },\n            [_vm._v(_vm._s(pkg.name))]\n          ),\n          _vm._v(\" \"),\n          _c(\n            \"div\",\n            { staticClass: \"fields\" },\n            _vm._l(pkg.resources, function(resource) {\n              return _c(\"span\", { key: resource.id }, [\n                _c(\"input\", {\n                  directives: [\n                    {\n                      name: \"model\",\n                      rawName: \"v-model\",\n                      value: _vm.resourceIds,\n                      expression: \"resourceIds\"\n                    }\n                  ],\n                  attrs: { type: \"checkbox\", id: resource.id },\n                  domProps: {\n                    value: resource.id,\n                    checked: Array.isArray(_vm.resourceIds)\n                      ? _vm._i(_vm.resourceIds, resource.id) > -1\n                      : _vm.resourceIds\n                  },\n                  on: {\n                    change: function($event) {\n                      var $$a = _vm.resourceIds,\n                        $$el = $event.target,\n                        $$c = $$el.checked ? true : false\n                      if (Array.isArray($$a)) {\n                        var $$v = resource.id,\n                          $$i = _vm._i($$a, $$v)\n                        if ($$el.checked) {\n                          $$i < 0 && (_vm.resourceIds = $$a.concat([$$v]))\n                        } else {\n                          $$i > -1 &&\n                            (_vm.resourceIds = $$a\n                              .slice(0, $$i)\n                              .concat($$a.slice($$i + 1)))\n                        }\n                      } else {\n                        _vm.resourceIds = $$c\n                      }\n                    }\n                  }\n                }),\n                _vm._v(\" \"),\n                _c(\"label\", { attrs: { for: resource.id } }, [\n                  _vm._v(_vm._s(resource.name))\n                ])\n              ])\n            }),\n            0\n          )\n        ])\n      })\n    ],\n    2\n  )\n}\nvar staticRenderFns = []\nrender._withStripped = true\n\n\n\n//# sourceURL=webpack://search/./src/components/ResourceList.vue?./node_modules/vue-loader/lib/loaders/templateLoader.js??vue-loader-options!./node_modules/vue-loader/lib??vue-loader-options");

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