(window.webpackJsonpsearch=window.webpackJsonpsearch||[]).push([[0],{702:function(e,t,n){var r=n(309),a=n(705);"string"==typeof(a=a.__esModule?a.default:a)&&(a=[[e.i,a,""]]);var i={insert:"head",singleton:!1};r(a,i);e.exports=a.locals||{}},704:function(e,t,n){"use strict";n(702)},705:function(e,t,n){(t=n(310)(!1)).push([e.i,"\ninput[data-v-fb38c1e2],\nselect[data-v-fb38c1e2] {\n  margin: 2px;\n}\n#radius[data-v-fb38c1e2] {\n  width: 45px;\n}\n#mapdisplay[data-v-fb38c1e2] {\n  height: 200px;\n  width: 100%;\n  margin-top: 5px;\n}\nsmall[data-v-fb38c1e2] {\n  text-align: left;\n  padding-right: 10px;\n}\n",""]),e.exports=t},706:function(e,t,n){"use strict";n.r(t);var r=function(){var e=this,t=e._self._c;return t("div",{staticClass:"term-editor floating flex-container flex-stretch-height"},[t("i",{staticClass:"fas fa-caret-square-left",attrs:{role:"button"},on:{click:e.closeDialog}}),e._v(" "),"geo"===e.fieldType?e._e():t("div",{staticClass:"term-editor-fields term-editor-block space-children-v"},[t("div",{staticClass:"flex-container flex-wrap flex-wrap-spacing field-list"},e._l(e.newFields,(function(n,r){return t("span",{key:n.id,staticClass:"fields"},[e._v("\n        "+e._s(n)+"\n        "),t("i",{staticClass:"delete-field fas fa-times-circle fa-xs",on:{click:function(){return e.deleteField(r)}}})])})),0),e._v(" "),t("FieldPicker",{attrs:{callback:e.addNewField,"resource-ids":e.resourceIds}})],1),e._v(" "),t("div",{staticClass:"term-editor-query term-editor-block space-children-v"},[t("div",{staticClass:"flex-container flex-nowrap flex-stretch-last"},[t("span",[e._v("As:")]),e._v(" "),t("select",{directives:[{name:"model",rawName:"v-model",value:e.fieldType,expression:"fieldType"}],attrs:{title:"Select what type to treat the field's contents as"},on:{change:[function(t){var n=Array.prototype.filter.call(t.target.options,(function(e){return e.selected})).map((function(e){return"_value"in e?e._value:e.value}));e.fieldType=t.target.multiple?n:n[0]},function(){e.comparisonType=e.schema.terms[e.fieldType][0]}]}},e._l(e.readableFieldTypes,(function(n,r){return t("option",{key:n.id,domProps:{value:r}},[e._v("\n          "+e._s(n)+"\n        ")])})),0)]),e._v(" "),t("div",{staticClass:"comparison-types flex-container flex-center"},e._l(e.terms,(function(n){return t("span",{key:n.id},[t("input",{directives:[{name:"model",rawName:"v-model",value:e.comparisonType,expression:"comparisonType"}],attrs:{type:"radio",id:n,name:"comparisonType",checked:""},domProps:{value:n,checked:e._q(e.comparisonType,n)},on:{change:function(){e.comparisonType=n}}}),e._v(" "),t("label",{attrs:{for:n}},[e._v(e._s(n))])])})),0),e._v(" "),t("div",{staticClass:"query-values"},[t("keep-alive",[t(e.fieldType,{tag:"component",attrs:{"comparison-type":e.comparisonType,"existing-term-id":e.existingTermId},on:{"set-query-values":e.setQueryValues,"pressed-enter":e.submitTerm}})],1)],1),e._v(" "),t("div",{staticClass:"flex-container flex-column flex-stretch-height"},[t("label",{staticClass:"sr-only",attrs:{for:"termNameInput"}},[e._v("Name (optional)")]),e._v(" "),t("input",{directives:[{name:"model",rawName:"v-model",value:e.termName,expression:"termName"}],attrs:{id:"termNameInput",type:"text",placeholder:"name (optional)"},domProps:{value:e.termName},on:{keyup:function(t){return!t.type.indexOf("key")&&e._k(t.keyCode,"enter",13,t.key,"Enter")?null:e.submitTerm.apply(null,arguments)},input:function(t){t.target.composing||(e.termName=t.target.value)}}})]),e._v(" "),t("div",{staticClass:"query-submit"},[t("button",{staticClass:"btn btn-primary no-icon",on:{click:e.submitTerm}},[e._v("\n        Save\n      ")])])])])};r._withStripped=!0;var a=n(18),i=n(2),s=function(){var e=this,t=e._self._c;return t("div",{staticClass:"flex-container flex-center"},[t("span",{staticClass:"fields"},[e._v(" field ")]),e._v(" "),t("label",{attrs:{for:"queryValueText"}},[t("i",{class:["fas","equals"===e.comparisonType?"fa-equals":"fa-search"]})]),e._v(" "),t("input",{directives:[{name:"model",rawName:"v-model",value:e.values[e.comparisonType].value,expression:"values[comparisonType].value"}],attrs:{type:"text",id:"queryValueText",size:"10"},domProps:{value:e.values[e.comparisonType].value},on:{keyup:function(t){return!t.type.indexOf("key")&&e._k(t.keyCode,"enter",13,t.key,"Enter")?null:e.pressedEnter.apply(null,arguments)},input:function(t){t.target.composing||e.$set(e.values[e.comparisonType],"value",t.target.value)}}})])};s._withStripped=!0;var o=function(){return(0,this._self._c)("div")};function l(e){return(l="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(e){return typeof e}:function(e){return e&&"function"==typeof Symbol&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e})(e)}function u(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(e);t&&(r=r.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,r)}return n}function c(e){for(var t,n=1;n<arguments.length;n++)t=null==arguments[n]?{}:arguments[n],n%2?u(Object(t),!0).forEach((function(n){p(e,n,t[n])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(t)):u(Object(t)).forEach((function(n){Object.defineProperty(e,n,Object.getOwnPropertyDescriptor(t,n))}));return e}function p(e,t,n){return(t=function(e){var t=function(e,t){if("object"!==l(e)||null===e)return e;var n=e[Symbol.toPrimitive];if(void 0!==n){var r=n.call(e,t||"default");if("object"!==l(r))return r;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"===l(t)?t:t+""}(t))in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}o._withStripped=!0;var d={name:"BaseEditor",props:["comparisonType","existingTermId"],data:function(){return{values:{}}},computed:c(c({},Object(i.c)("results/query/filters",["getFilterById"])),{},{queryValues:function(){return this.values[this.comparisonType]}}),created:function(){this.loadExisting()},methods:{loadExisting:function(){var e=this;if(void 0!==this.existingTermId){var t=this.getFilterById(this.existingTermId);a.b(this.values[this.comparisonType]).forEach((function(n){e.$set(e.values[e.comparisonType],n,t.content[n]||null)}))}},pressedEnter:function(){this.$emit("pressed-enter")}},watch:{values:{handler:function(){this.$emit("set-query-values",this.queryValues)},deep:!0}}},m=n(5),v=Object(m.a)(d,o,[],!1,null,null,null).exports,f={extends:v,name:"TextEditor",data:function(){return{values:{equals:{value:null},contains:{value:null}}}}},y=Object(m.a)(f,s,[],!1,null,null,null).exports,h=function(){var e=this,t=e._self._c;return t("div",{staticClass:"flex-container flex-center"},["range"===e.comparisonType?t("span",[t("input",{directives:[{name:"model",rawName:"v-model",value:e.values.range.greater_than,expression:"values.range.greater_than"}],attrs:{type:"number"},domProps:{value:e.values.range.greater_than},on:{keyup:function(t){return!t.type.indexOf("key")&&e._k(t.keyCode,"enter",13,t.key,"Enter")?null:e.pressedEnter.apply(null,arguments)},input:function(t){t.target.composing||e.$set(e.values.range,"greater_than",t.target.value)}}}),e._v(" "),t("input",{directives:[{name:"model",rawName:"v-model",value:e.values.range.greater_than_inclusive,expression:"values.range.greater_than_inclusive"}],attrs:{type:"checkbox",id:"greaterThanEq"},domProps:{checked:Array.isArray(e.values.range.greater_than_inclusive)?-1<e._i(e.values.range.greater_than_inclusive,null):e.values.range.greater_than_inclusive},on:{change:function(t){var n=e.values.range.greater_than_inclusive,r=t.target,a=!!r.checked;if(Array.isArray(n)){var i=e._i(n,null);r.checked?0>i&&e.$set(e.values.range,"greater_than_inclusive",n.concat([null])):-1<i&&e.$set(e.values.range,"greater_than_inclusive",n.slice(0,i).concat(n.slice(i+1)))}else e.$set(e.values.range,"greater_than_inclusive",a)}}}),e._v(" "),"range"===e.comparisonType?t("label",{attrs:{for:"greaterThanEq"}},[t("i",{class:["fas","fa-less-than"+(e.values.range.greater_than_inclusive?"-equal":"")]})]):e._e()]):e._e(),e._v(" "),t("span",{staticClass:"fields"},[e._v(" field ")]),e._v(" "),"range"===e.comparisonType?t("span",[t("input",{directives:[{name:"model",rawName:"v-model",value:e.values.range.less_than_inclusive,expression:"values.range.less_than_inclusive"}],attrs:{type:"checkbox",id:"lessThanEq"},domProps:{checked:Array.isArray(e.values.range.less_than_inclusive)?-1<e._i(e.values.range.less_than_inclusive,null):e.values.range.less_than_inclusive},on:{change:function(t){var n=e.values.range.less_than_inclusive,r=t.target,a=!!r.checked;if(Array.isArray(n)){var i=e._i(n,null);r.checked?0>i&&e.$set(e.values.range,"less_than_inclusive",n.concat([null])):-1<i&&e.$set(e.values.range,"less_than_inclusive",n.slice(0,i).concat(n.slice(i+1)))}else e.$set(e.values.range,"less_than_inclusive",a)}}}),e._v(" "),t("label",{attrs:{for:"lessThanEq"}},[t("i",{class:["fas","fa-less-than"+(e.values.range.less_than_inclusive?"-equal":"")]})]),e._v(" "),t("input",{directives:[{name:"model",rawName:"v-model",value:e.values.range.less_than,expression:"values.range.less_than"}],attrs:{type:"number"},domProps:{value:e.values.range.less_than},on:{keyup:function(t){return!t.type.indexOf("key")&&e._k(t.keyCode,"enter",13,t.key,"Enter")?null:e.pressedEnter.apply(null,arguments)},input:function(t){t.target.composing||e.$set(e.values.range,"less_than",t.target.value)}}})]):e._e(),e._v(" "),"equals"===e.comparisonType?t("span",[e._m(0),e._v(" "),"equals"===e.comparisonType?t("input",{directives:[{name:"model",rawName:"v-model",value:e.values.equals.value,expression:"values.equals.value"}],attrs:{type:"number",id:"queryValueInt1"},domProps:{value:e.values.equals.value},on:{keyup:function(t){return!t.type.indexOf("key")&&e._k(t.keyCode,"enter",13,t.key,"Enter")?null:e.pressedEnter.apply(null,arguments)},input:function(t){t.target.composing||e.$set(e.values.equals,"value",t.target.value)}}}):e._e()]):e._e()])};h._withStripped=!0;var g={extends:v,name:"NumberEditor",data:function(){return{values:{equals:{value:null},range:{greater_than:null,less_than:null,greater_than_inclusive:null,less_than_inclusive:null}}}},computed:{queryValues:function(){var e=this;return a.b(this.values[this.comparisonType]).forEach((function(t){var n=e.values[e.comparisonType][t];["value","less_than","greater_than"].includes(t)&&null!==e.values[e.comparisonType][t]&&e.$set(e.values[e.comparisonType],t,+n)})),this.values[this.comparisonType]}}},_=Object(m.a)(g,h,[function(){var e=this._self._c;return e("label",{attrs:{for:"queryValueInt1"}},[e("i",{staticClass:"fas fa-equals"})])}],!1,null,null,null).exports,b=function(){var e=this,t=e._self._c;return t("div",{staticClass:"flex-container flex-column flex-center"},["point"===e.comparisonType?t("div",{staticClass:"flex-container flex-center"},[t("input",{directives:[{name:"model",rawName:"v-model",value:e.values.point.latitude,expression:"values.point.latitude"}],attrs:{type:"text",title:"Latitude",size:"3"},domProps:{value:e.values.point.latitude},on:{keyup:function(t){return!t.type.indexOf("key")&&e._k(t.keyCode,"enter",13,t.key,"Enter")?null:e.pressedEnter.apply(null,arguments)},input:function(t){t.target.composing||e.$set(e.values.point,"latitude",t.target.value)}}}),e._v(" "),t("span",[e._v(",")]),e._v(" "),t("input",{directives:[{name:"model",rawName:"v-model",value:e.values.point.longitude,expression:"values.point.longitude"}],attrs:{type:"text",title:"Longitude",size:"3"},domProps:{value:e.values.point.longitude},on:{keyup:function(t){return!t.type.indexOf("key")&&e._k(t.keyCode,"enter",13,t.key,"Enter")?null:e.pressedEnter.apply(null,arguments)},input:function(t){t.target.composing||e.$set(e.values.point,"longitude",t.target.value)}}}),e._v(" "),t("label",{attrs:{for:"radius"}},[e._v("±")]),e._v(" "),t("input",{directives:[{name:"model",rawName:"v-model.number",value:e.values.point.radius,expression:"values.point.radius",modifiers:{number:!0}}],attrs:{type:"number",title:"Radius",min:"0",id:"radius"},domProps:{value:e.values.point.radius},on:{keyup:function(t){return!t.type.indexOf("key")&&e._k(t.keyCode,"enter",13,t.key,"Enter")?null:e.pressedEnter.apply(null,arguments)},input:function(t){t.target.composing||e.$set(e.values.point,"radius",e._n(t.target.value))},blur:function(){return e.$forceUpdate()}}}),e._v(" "),t("select",{directives:[{name:"model",rawName:"v-model",value:e.values.point.radius_unit,expression:"values.point.radius_unit"}],attrs:{title:"Radius units"},on:{change:function(t){var n=Array.prototype.filter.call(t.target.options,(function(e){return e.selected})).map((function(e){return"_value"in e?e._value:e.value}));e.$set(e.values.point,"radius_unit",t.target.multiple?n:n[0])}}},e._l(e.radiusUnits,(function(n){return t("option",{key:n.id},[e._v(e._s(n))])})),0)]):e._e(),e._v(" "),"named_area"===e.comparisonType?t("div",{staticClass:"flex-container flex-center flex-column"},[t("span",[t("label",{attrs:{for:"geoCategory"}},[e._v("Category")]),e._v(" "),t("select",{directives:[{name:"model",rawName:"v-model",value:e.geoCategory,expression:"geoCategory"}],attrs:{id:"geoCategory"},on:{change:function(t){var n=Array.prototype.filter.call(t.target.options,(function(e){return e.selected})).map((function(e){return"_value"in e?e._value:e.value}));e.geoCategory=t.target.multiple?n:n[0]}}},e._l(e.namedAreas,(function(n,r){return t("option",{key:r.id},[e._v("\n          "+e._s(r)+"\n        ")])})),0)]),e._v(" "),t("span",[t("label",{attrs:{for:"geoName"}},[e._v("Name")]),e._v(" "),t("select",{directives:[{name:"model",rawName:"v-model",value:e.values.named_area[e.geoCategory],expression:"values.named_area[geoCategory]"}],attrs:{id:"geoName",disabled:!e.geoCategory},on:{change:function(t){var n=Array.prototype.filter.call(t.target.options,(function(e){return e.selected})).map((function(e){return"_value"in e?e._value:e.value}));e.$set(e.values.named_area,e.geoCategory,t.target.multiple?n:n[0])}}},e._l(e.namedAreas[e.geoCategory]||[],(function(n){return t("option",{key:n.id},[e._v("\n          "+e._s(n)+"\n        ")])})),0)])]):e._e(),e._v(" "),"custom_area"===e.comparisonType?t("div",{staticClass:"flex-container flex-center flex-column flex-stretch-height space-children-v full-width"},[t("div",{staticClass:"flex-container flex-wrap flex-wrap-spacing"},[e._l(e.values.custom_area,(function(n,r){return t("span",{key:n.id,staticClass:"fields"},[e._v("\n        "+e._s(n.map((function(e){return e.length})).reduce((function(e,t){return e+t}),0))+" points\n        "),t("i",{staticClass:"delete-field fas fa-times-circle fa-xs",on:{click:function(){return e.deletePolygon(r)}}})])})),e._v(" "),t("i",{staticClass:"fas fa-plus-square",attrs:{title:"Add new polygon",role:"button"},on:{click:e.addPolygon}})],2),e._v(" "),t("div",{staticClass:"flex-container"},[e._m(0),e._v(" "),t("label",{attrs:{for:"useGeoJson"}},[e._v("Paste GeoJSON")]),e._v(" "),t("input",{directives:[{name:"model",rawName:"v-model",value:e.useGeoJson,expression:"useGeoJson"}],attrs:{type:"checkbox",id:"useGeoJson"},domProps:{checked:Array.isArray(e.useGeoJson)?-1<e._i(e.useGeoJson,null):e.useGeoJson},on:{change:function(t){var n=e.useGeoJson,r=t.target,a=!!r.checked;if(Array.isArray(n)){var i=e._i(n,null);r.checked?0>i&&(e.useGeoJson=n.concat([null])):-1<i&&(e.useGeoJson=n.slice(0,i).concat(n.slice(i+1)))}else e.useGeoJson=a}}})]),e._v(" "),e.useGeoJson?t("textarea",{directives:[{name:"model",rawName:"v-model",value:e.pastedGeoJson,expression:"pastedGeoJson"}],attrs:{placeholder:"Paste a list of MultiPolygon coordinates, e.g. [[[[1, 1], [0, 0], [1, 0], [1, 1]]]]"},domProps:{value:e.pastedGeoJson},on:{input:function(t){t.target.composing||(e.pastedGeoJson=t.target.value)}}}):e._e(),e._v(" "),t("button",{staticClass:"btn btn-primary",on:{click:e.parseGeoJson}},[e._v("Set")])]):e._e(),e._v(" "),"named_area"===e.comparisonType?e._e():t("div",{attrs:{id:"mapdisplay"}})])};b._withStripped=!0;var k=n(703),x=n.n(k);function T(e){return(T="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(e){return typeof e}:function(e){return e&&"function"==typeof Symbol&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e})(e)}function O(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(e);t&&(r=r.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,r)}return n}function w(e){for(var t,n=1;n<arguments.length;n++)t=null==arguments[n]?{}:arguments[n],n%2?O(Object(t),!0).forEach((function(n){P(e,n,t[n])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(t)):O(Object(t)).forEach((function(n){Object.defineProperty(e,n,Object.getOwnPropertyDescriptor(t,n))}));return e}function P(e,t,n){return(t=function(e){var t=function(e,t){if("object"!==T(e)||null===e)return e;var n=e[Symbol.toPrimitive];if(void 0!==n){var r=n.call(e,t||"default");if("object"!==T(r))return r;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"===T(t)?t:t+""}(t))in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}var j={extends:v,name:"GeoEditor",data:function(){return{values:{point:{latitude:null,longitude:null,radius:0,radius_unit:"mi"},named_area:{country:null,marine:null,geography:null},custom_area:[[]]},geoCategory:null,leafletMap:null,markers:{point:{group:x.a.layerGroup(),circle:x.a.circle(),marker:x.a.marker()},named_area:{group:x.a.layerGroup(),data:null},custom_area:{group:x.a.layerGroup()}},pastedGeoJson:null,currentPolygon:[],useGeoJson:!1,mapInitialised:!1}},computed:w(w({},Object(i.e)(["schema"])),{},{radiusUnits:function(){return this.schema.raw.definitions.term.properties.geo_point.properties.radius_unit.enum},namedAreas:function(){return a.c().key((function(e){return e.key})).rollup((function(e){return e[0].value.enum})).object(a.a(this.schema.raw.definitions.term.properties.geo_named_area.properties))},radiusMeters:function(){return{mi:function(e){return e/62137e-8},yd:function(e){return e/1.0936},ft:function(e){return e/3.2808},in:function(e){return e/39.37},km:function(e){return 1e3*e},m:function(e){return e},cm:function(e){return e/100},mm:function(e){return e/1e3},nmi:function(e){return e/53996e-8}}[this.values.point.radius_unit](this.values.point.radius)}}),methods:{loadExisting:function(){var e=this;if(void 0!==this.existingTermId){var t=this.getFilterById(this.existingTermId);"custom_area"===this.comparisonType?this.$set(this.values,"custom_area",t.content):a.b(this.values[this.comparisonType]).forEach((function(n){e.$set(e.values[e.comparisonType],n,t.content[n]||null)})),"named_area"===this.comparisonType&&(this.geoCategory=a.b(t.content).filter((function(t){return a.b(e.namedAreas).includes(t)}))[0])}},setLatLng:function(e){if("point"===this.comparisonType&&(this.$set(this.values.point,"latitude",e.latlng.lat),this.$set(this.values.point,"longitude",e.latlng.lng)),"custom_area"===this.comparisonType){if(this.useGeoJson)return;var t=[e.latlng.lng,e.latlng.lat];0===this.currentPolygon.length?(this.currentPolygon.push(t),this.currentPolygon.push(t)):this.currentPolygon.splice(this.currentPolygon.length-1,0,t),this.$set(this.values.custom_area,this.values.custom_area.length-1,[this.currentPolygon])}},resetMap:function(){var e=this;a.d(this.markers).forEach((function(t){e.leafletMap.hasLayer(t.group)&&e.leafletMap.removeLayer(t.group)})),this.markers[this.comparisonType].group.addTo(this.leafletMap),this.leafletMap.on("click",this.setLatLng)},parseGeoJson:function(){if(null!==this.pastedGeoJson){var e=[],t=!0;try{e=JSON.parse(this.pastedGeoJson)}catch(e){t=!1,console.log("Invalid JSON.")}t&&this.$set(this.values,"custom_area",e)}},setGeoJson:function(){this.markers.custom_area.group.clearLayers();try{var e={type:"MultiPolygon",coordinates:this.values.custom_area};this.markers.custom_area.group.addLayer(x.a.geoJSON(e))}catch(e){console.log(e),this.markers.custom_area.group.addLayer(x.a.popup().setLatLng(this.leafletMap.getCenter()).setContent("Invalid GeoJSON."))}},addPolygon:function(){this.pastedGeoJson=null,this.currentPolygon=[],this.values.custom_area.push([])},deletePolygon:function(e){this.$delete(this.values.custom_area,e)},initMap:function(){this.leafletMap=x.a.map("mapdisplay"),this.leafletMap.setView([0,0],0),x.a.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",{maxZoom:18}).addTo(this.leafletMap),this.resetMap(),this.mapInitialised=!0}},mounted:function(){"named_area"!==this.comparisonType&&this.initMap()},watch:{comparisonType:function(){"named_area"===this.comparisonType||(this.mapInitialised?this.resetMap():setTimeout(this.initMap,1e3))},"values.point":{handler:function(){var e=[this.values.point.latitude,this.values.point.longitude];return e.some((function(e){return null===e||""===e}))?void this.markers.point.group.clearLayers():(this.leafletMap.setView(e),this.markers.point.marker.setLatLng(e),!this.markers.point.group.hasLayer(this.markers.point.marker)&&this.markers.point.group.addLayer(this.markers.point.marker),void(0<this.values.point.radius?(this.markers.point.circle.setLatLng(e),this.markers.point.circle.setRadius(this.radiusMeters),!this.markers.point.group.hasLayer(this.markers.point.circle)&&this.markers.point.group.addLayer(this.markers.point.circle)):this.markers.point.group.removeLayer(this.markers.point.circle)))},deep:!0},"values.named_area":{handler:function(e){var t=this,n=a.a(e);1<n.map((function(e){return null===e.value?0:1})).reduce((function(e,t){return e+t}))&&n.forEach((function(e){t.$set(t.values.named_area,e.key,null)}))},deep:!0},"values.custom_area":{handler:function(){this.pastedGeoJson=JSON.stringify(this.values.custom_area),this.setGeoJson()},deep:!0}}},C=(n(704),Object(m.a)(j,b,[function(){var e=this,t=e._self._c;return t("small",[e._v("\n        Click on the map to add polygon points. Try\n        "),t("a",{attrs:{id:"geojson-link",href:"https://geojson.net"}},[e._v("geojson.net")]),e._v(" for\n        editing more complex MultiPolygon queries.\n      ")])}],!1,null,"fb38c1e2",null).exports),q=function(){return(0,this._self._c)("div",{staticClass:"flex-container flex-center"})};q._withStripped=!0;var S={extends:v,name:"OtherEditor",data:function(){return{values:{}}}},E=Object(m.a)(S,q,[],!1,null,null,null).exports;function N(e){return(N="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(e){return typeof e}:function(e){return e&&"function"==typeof Symbol&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e})(e)}function J(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(e);t&&(r=r.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,r)}return n}function G(e){for(var t,n=1;n<arguments.length;n++)t=null==arguments[n]?{}:arguments[n],n%2?J(Object(t),!0).forEach((function(n){I(e,n,t[n])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(t)):J(Object(t)).forEach((function(n){Object.defineProperty(e,n,Object.getOwnPropertyDescriptor(t,n))}));return e}function I(e,t,n){return(t=function(e){var t=function(e,t){if("object"!==N(e)||null===e)return e;var n=e[Symbol.toPrimitive];if(void 0!==n){var r=n.call(e,t||"default");if("object"!==N(r))return r;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"===N(t)?t:t+""}(t))in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function A(e){return function(e){if(Array.isArray(e))return $(e)}(e)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(e)||function(e,t){if(e){if("string"==typeof e)return $(e,t);var n=Object.prototype.toString.call(e).slice(8,-1);return"Object"===n&&e.constructor&&(n=e.constructor.name),"Map"===n||"Set"===n?Array.from(e):"Arguments"===n||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)?$(e,t):void 0}}(e)||function(){throw new TypeError("Invalid attempt to spread non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()}function $(e,t){(null==t||t>e.length)&&(t=e.length);for(var n=0,r=Array(t);n<t;n++)r[n]=e[n];return r}var L={name:"TermEditor",components:{FieldPicker:n(299).a,string:y,number:_,geo:C,other:E},props:["existingTermId","parentId"],data:function(){var e={newFields:[],fieldType:"string",comparisonType:"equals",termName:null,queryValues:{},readableFieldTypes:{string:"Text",number:"Number",geo:"Geo",other:"Any"}};if(void 0!==this.existingTermId){var t=this.$store.getters["results/query/filters/getFilterById"](this.existingTermId);e.newFields=A(t.content.fields||[]),e.fieldType=t.key.includes("_")?t.key.split("_")[0]:"other",e.comparisonType=t.key.slice(t.key.indexOf("_")+1),e.termName=t.display.name}return e},computed:G(G(G(G({},Object(i.e)(["schema"])),Object(i.e)("results/query/resources",["resourceIds"])),Object(i.c)("results/query/filters",["getFilterById"])),{},{terms:function(){var e=this.schema.terms[this.fieldType];return 1===e.length&&(""===e[0]||null===e[0])?[]:e},queryType:function(){return"other"===this.fieldType?this.comparisonType:[this.fieldType,this.comparisonType].join("_")},query:function(){var e={};return"geo"!==this.fieldType&&(e.fields=this.newFields),Array.isArray(this.queryValues)?e=this.queryValues:a.a(this.queryValues).forEach((function(t){null!==t.value&&(e[t.key]=t.value)})),e}}),methods:G(G(G({},Object(i.d)("results/query/filters",["changeKey","changeContent","changeName"])),Object(i.b)("results/query/filters",["addTerm"])),{},{setQueryValues:function(e){this.queryValues=e},addNewField:function(e){this.newFields.push(e)},deleteField:function(e){this.$delete(this.newFields,e)},closeDialog:function(){this.$parent.showEditor=!1},submitTerm:function(){void 0===this.existingTermId?this.addTerm({parent:this.parentId,key:this.queryType,content:this.query,display:{name:this.termName}}):(this.changeKey({key:this.queryType,id:this.existingTermId}),this.changeContent({content:this.query,id:this.existingTermId}),this.changeName({name:this.termName,id:this.existingTermId})),this.closeDialog()},resetQuery:function(){this.queryValues={}}}),watch:{fieldType:function(){this.resetQuery()},comparisonType:function(){this.resetQuery()}}},M=Object(m.a)(L,r,[],!1,null,null,null);t.default=M.exports}}]);