(window.webpackJsonpsearch=window.webpackJsonpsearch||[]).push([[0],{567:function(e,t,n){var a=n(570);"string"==typeof a&&(a=[[e.i,a,""]]);var r={insert:"head",singleton:!1};n(244)(a,r);a.locals&&(e.exports=a.locals)},569:function(e,t,n){"use strict";var a=n(567);n.n(a).a},570:function(e,t,n){(e.exports=n(243)(!1)).push([e.i,"\ninput[data-v-0427c375], select[data-v-0427c375] {\n    margin: 2px;\n}\n#radius[data-v-0427c375] {\n    width: 45px;\n}\n#mapdisplay[data-v-0427c375] {\n    height: 200px;\n    width: 100%;\n    margin-top: 5px;\n}\nsmall[data-v-0427c375] {\n    text-align: left;\n    padding-right: 10px;\n}\n",""])},571:function(e,t,n){"use strict";n.r(t);var a=function(){var e=this,t=e.$createElement,n=e._self._c||t;return n("div",{staticClass:"term-editor floating flex-container flex-smallwrap flex-stretch-height"},[n("i",{staticClass:"fas fa-caret-square-left",attrs:{role:"button"},on:{click:e.closeDialog}}),e._v(" "),"geo"!==e.fieldType?n("div",{staticClass:"term-editor-fields space-children-v"},[n("div",{staticClass:"flex-container flex-wrap flex-wrap-spacing"},e._l(e.newFields,(function(t,a){return n("span",{key:t.id,staticClass:"fields"},[e._v("\n                            "+e._s(t)+"\n                            "),n("i",{staticClass:"delete-field fas fa-times-circle fa-xs",on:{click:function(t){return e.deleteField(a)}}})])})),0),e._v(" "),n("FieldPicker",{attrs:{callback:e.addNewField,"resource-ids":e.resourceIds}})],1):e._e(),e._v(" "),n("div",{staticClass:"term-editor-query space-children-v"},[n("div",{staticClass:"flex-container flex-nowrap flex-stretch-last"},[n("span",[e._v("As:")]),e._v(" "),n("select",{directives:[{name:"model",rawName:"v-model",value:e.fieldType,expression:"fieldType"}],attrs:{title:"Select what type to treat the field's contents as"},on:{change:[function(t){var n=Array.prototype.filter.call(t.target.options,(function(e){return e.selected})).map((function(e){return"_value"in e?e._value:e.value}));e.fieldType=t.target.multiple?n:n[0]},function(t){e.comparisonType=e.schema.terms[e.fieldType][0]}]}},e._l(e.readableFieldTypes,(function(t,a){return n("option",{key:t.id,domProps:{value:a}},[e._v(e._s(t)+"\n            ")])})),0)]),e._v(" "),n("div",{staticClass:"comparison-types flex-container flex-center"},e._l(e.terms,(function(t){return n("span",{key:t.id},[n("input",{directives:[{name:"model",rawName:"v-model",value:e.comparisonType,expression:"comparisonType"}],attrs:{type:"radio",id:t,name:"comparisonType",checked:""},domProps:{value:t,checked:e._q(e.comparisonType,t)},on:{change:function(n){e.comparisonType=t}}}),e._v(" "),n("label",{attrs:{for:t}},[e._v(e._s(t))])])})),0),e._v(" "),n("div",{staticClass:"query-values"},[n("keep-alive",[n(e.fieldType,{tag:"component",attrs:{"comparison-type":e.comparisonType,"existing-term-id":e.existingTermId},on:{"set-query-values":e.setQueryValues}})],1)],1),e._v(" "),n("div",{staticClass:"flex-container flex-column flex-stretch-height"},[n("span",[n("label",{attrs:{for:"termNameInput"}},[e._v("Name (optional)")]),e._v(" "),n("input",{directives:[{name:"model",rawName:"v-model",value:e.termName,expression:"termName"}],attrs:{id:"termNameInput",type:"text"},domProps:{value:e.termName},on:{input:function(t){t.target.composing||(e.termName=t.target.value)}}})])]),e._v(" "),n("div",{staticClass:"query-submit"},[n("button",{staticClass:"btn btn-primary no-icon",on:{click:e.submitTerm}},[e._v("Save")])])])])};a._withStripped=!0;var r=n(12),s=n(2),i=function(){var e=this,t=e.$createElement,n=e._self._c||t;return n("div",{staticClass:"flex-container flex-center"},[n("span",{staticClass:"fields"},[e._v("\n                    field\n                ")]),e._v(" "),n("label",{attrs:{for:"queryValueText"}},[n("i",{class:["fas","equals"===e.comparisonType?"fa-equals":"fa-search"]})]),e._v(" "),n("input",{directives:[{name:"model",rawName:"v-model",value:e.values[e.comparisonType].value,expression:"values[comparisonType].value"}],attrs:{type:"text",id:"queryValueText",size:"10"},domProps:{value:e.values[e.comparisonType].value},on:{input:function(t){t.target.composing||e.$set(e.values[e.comparisonType],"value",t.target.value)}}})])};i._withStripped=!0;var o=function(){var e=this.$createElement;return(this._self._c||e)("div")};function l(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(e);t&&(a=a.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,a)}return n}function u(e){for(var t,n=1;n<arguments.length;n++)t=null==arguments[n]?{}:arguments[n],n%2?l(Object(t),!0).forEach((function(n){c(e,n,t[n])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(t)):l(Object(t)).forEach((function(n){Object.defineProperty(e,n,Object.getOwnPropertyDescriptor(t,n))}));return e}function c(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}o._withStripped=!0;var p={name:"BaseEditor",props:["comparisonType","existingTermId"],data:function(){return{values:{}}},computed:u(u({},Object(s.c)("results/query/filters",["getFilterById"])),{},{queryValues:function(){return this.values[this.comparisonType]}}),created:function(){this.loadExisting()},methods:{loadExisting:function(){var e=this;if(void 0!==this.existingTermId){var t=this.getFilterById(this.existingTermId);r.b(this.values[this.comparisonType]).forEach((function(n){e.$set(e.values[e.comparisonType],n,t.content[n]||null)}))}}},watch:{values:{handler:function(){this.$emit("set-query-values",this.queryValues)},deep:!0}}},d=n(4),v=Object(d.a)(p,o,[],!1,null,null,null);v.options.__file="src/components/editors/BaseEditor.vue";var m=v.exports,h={extends:m,name:"TextEditor",data:function(){return{values:{equals:{value:null},contains:{value:null}}}}},f=Object(d.a)(h,i,[],!1,null,null,null);f.options.__file="src/components/editors/TextEditor.vue";var g=f.exports,y=function(){var e=this,t=e.$createElement,n=e._self._c||t;return n("div",{staticClass:"flex-container flex-center"},["range"===e.comparisonType?n("span",[n("input",{directives:[{name:"model",rawName:"v-model",value:e.values.range.greater_than,expression:"values.range.greater_than"}],attrs:{type:"number"},domProps:{value:e.values.range.greater_than},on:{input:function(t){t.target.composing||e.$set(e.values.range,"greater_than",t.target.value)}}}),e._v(" "),n("input",{directives:[{name:"model",rawName:"v-model",value:e.values.range.greater_than_inclusive,expression:"values.range.greater_than_inclusive"}],attrs:{type:"checkbox",id:"greaterThanEq"},domProps:{checked:Array.isArray(e.values.range.greater_than_inclusive)?e._i(e.values.range.greater_than_inclusive,null)>-1:e.values.range.greater_than_inclusive},on:{change:function(t){var n=e.values.range.greater_than_inclusive,a=t.target,r=!!a.checked;if(Array.isArray(n)){var s=e._i(n,null);a.checked?s<0&&e.$set(e.values.range,"greater_than_inclusive",n.concat([null])):s>-1&&e.$set(e.values.range,"greater_than_inclusive",n.slice(0,s).concat(n.slice(s+1)))}else e.$set(e.values.range,"greater_than_inclusive",r)}}}),e._v(" "),"range"===e.comparisonType?n("label",{attrs:{for:"greaterThanEq"}},[n("i",{class:["fas","fa-less-than"+(e.values.range.greater_than_inclusive?"-equal":"")]})]):e._e()]):e._e(),e._v(" "),n("span",{staticClass:"fields"},[e._v("\n        field\n    ")]),e._v(" "),"range"===e.comparisonType?n("span",[n("input",{directives:[{name:"model",rawName:"v-model",value:e.values.range.less_than_inclusive,expression:"values.range.less_than_inclusive"}],attrs:{type:"checkbox",id:"lessThanEq"},domProps:{checked:Array.isArray(e.values.range.less_than_inclusive)?e._i(e.values.range.less_than_inclusive,null)>-1:e.values.range.less_than_inclusive},on:{change:function(t){var n=e.values.range.less_than_inclusive,a=t.target,r=!!a.checked;if(Array.isArray(n)){var s=e._i(n,null);a.checked?s<0&&e.$set(e.values.range,"less_than_inclusive",n.concat([null])):s>-1&&e.$set(e.values.range,"less_than_inclusive",n.slice(0,s).concat(n.slice(s+1)))}else e.$set(e.values.range,"less_than_inclusive",r)}}}),e._v(" "),n("label",{attrs:{for:"lessThanEq"}},[n("i",{class:["fas","fa-less-than"+(e.values.range.less_than_inclusive?"-equal":"")]})]),e._v(" "),n("input",{directives:[{name:"model",rawName:"v-model",value:e.values.range.less_than,expression:"values.range.less_than"}],attrs:{type:"number"},domProps:{value:e.values.range.less_than},on:{input:function(t){t.target.composing||e.$set(e.values.range,"less_than",t.target.value)}}})]):e._e(),e._v(" "),"equals"===e.comparisonType?n("span",[e._m(0),e._v(" "),"equals"===e.comparisonType?n("input",{directives:[{name:"model",rawName:"v-model",value:e.values.equals.value,expression:"values.equals.value"}],attrs:{type:"number",id:"queryValueInt1"},domProps:{value:e.values.equals.value},on:{input:function(t){t.target.composing||e.$set(e.values.equals,"value",t.target.value)}}}):e._e()]):e._e()])};y._withStripped=!0;var _={extends:m,name:"NumberEditor",data:function(){return{values:{equals:{value:null},range:{greater_than:null,less_than:null,greater_than_inclusive:null,less_than_inclusive:null}}}},computed:{queryValues:function(){var e=this;return r.b(this.values[this.comparisonType]).forEach((function(t){var n=e.values[e.comparisonType][t];["value","less_than","greater_than"].includes(t)&&null!==e.values[e.comparisonType][t]&&e.$set(e.values[e.comparisonType],t,+n)})),this.values[this.comparisonType]}}},b=Object(d.a)(_,y,[function(){var e=this.$createElement,t=this._self._c||e;return t("label",{attrs:{for:"queryValueInt1"}},[t("i",{staticClass:"fas fa-equals"})])}],!1,null,null,null);b.options.__file="src/components/editors/NumberEditor.vue";var x=b.exports,T=function(){var e=this,t=e.$createElement,n=e._self._c||t;return n("div",{staticClass:"flex-container flex-column flex-center"},["point"===e.comparisonType?n("div",{staticClass:"flex-container flex-center"},[n("input",{directives:[{name:"model",rawName:"v-model",value:e.values.point.latitude,expression:"values.point.latitude"}],attrs:{type:"text",title:"Latitude",size:"3"},domProps:{value:e.values.point.latitude},on:{input:function(t){t.target.composing||e.$set(e.values.point,"latitude",t.target.value)}}}),e._v(" "),n("span",[e._v(",")]),e._v(" "),n("input",{directives:[{name:"model",rawName:"v-model",value:e.values.point.longitude,expression:"values.point.longitude"}],attrs:{type:"text",title:"Longitude",size:"3"},domProps:{value:e.values.point.longitude},on:{input:function(t){t.target.composing||e.$set(e.values.point,"longitude",t.target.value)}}}),e._v(" "),n("label",{attrs:{for:"radius"}},[e._v("±")]),e._v(" "),n("input",{directives:[{name:"model",rawName:"v-model",value:e.values.point.radius,expression:"values.point.radius"}],attrs:{type:"number",title:"Radius",min:"0",id:"radius"},domProps:{value:e.values.point.radius},on:{input:function(t){t.target.composing||e.$set(e.values.point,"radius",t.target.value)}}}),e._v(" "),n("select",{directives:[{name:"model",rawName:"v-model",value:e.values.point.radius_unit,expression:"values.point.radius_unit"}],attrs:{title:"Radius units"},on:{change:function(t){var n=Array.prototype.filter.call(t.target.options,(function(e){return e.selected})).map((function(e){return"_value"in e?e._value:e.value}));e.$set(e.values.point,"radius_unit",t.target.multiple?n:n[0])}}},e._l(e.radiusUnits,(function(t){return n("option",{key:t.id},[e._v(e._s(t)+"\n            ")])})),0)]):e._e(),e._v(" "),"named_area"===e.comparisonType?n("div",{staticClass:"flex-container flex-center flex-column"},[n("span",[n("label",{attrs:{for:"geoCategory"}},[e._v("Category")]),e._v(" "),n("select",{directives:[{name:"model",rawName:"v-model",value:e.geoCategory,expression:"geoCategory"}],attrs:{id:"geoCategory"},on:{change:function(t){var n=Array.prototype.filter.call(t.target.options,(function(e){return e.selected})).map((function(e){return"_value"in e?e._value:e.value}));e.geoCategory=t.target.multiple?n:n[0]}}},e._l(e.namedAreas,(function(t,a){return n("option",{key:a.id},[e._v(e._s(a)+"\n                ")])})),0)]),e._v(" "),n("span",[n("label",{attrs:{for:"geoName"}},[e._v("Name")]),e._v(" "),n("select",{directives:[{name:"model",rawName:"v-model",value:e.values.named_area[e.geoCategory],expression:"values.named_area[geoCategory]"}],attrs:{id:"geoName",disabled:!e.geoCategory},on:{change:function(t){var n=Array.prototype.filter.call(t.target.options,(function(e){return e.selected})).map((function(e){return"_value"in e?e._value:e.value}));e.$set(e.values.named_area,e.geoCategory,t.target.multiple?n:n[0])}}},e._l(e.namedAreas[e.geoCategory]||[],(function(t){return n("option",{key:t.id},[e._v("\n                    "+e._s(t)+"\n                ")])})),0)])]):e._e(),e._v(" "),"custom_area"===e.comparisonType?n("div",{staticClass:"flex-container flex-center flex-column flex-stretch-height space-children-v full-width"},[n("div",{staticClass:"flex-container flex-wrap flex-wrap-spacing"},[e._l(e.values.custom_area,(function(t,a){return n("span",{key:t.id,staticClass:"fields"},[e._v("\n                "+e._s(t.map((function(e){return e.length})).reduce((function(e,t){return e+t}),0))+" points\n                "),n("i",{staticClass:"delete-field fas fa-times-circle fa-xs",on:{click:function(t){return e.deletePolygon(a)}}})])})),e._v(" "),n("i",{staticClass:"fas fa-plus-square",attrs:{title:"Add new polygon",role:"button"},on:{click:e.addPolygon}})],2),e._v(" "),n("div",{staticClass:"flex-container"},[e._m(0),e._v(" "),n("label",{attrs:{for:"useGeoJson"}},[e._v("Paste GeoJSON")]),e._v(" "),n("input",{directives:[{name:"model",rawName:"v-model",value:e.useGeoJson,expression:"useGeoJson"}],attrs:{type:"checkbox",id:"useGeoJson"},domProps:{checked:Array.isArray(e.useGeoJson)?e._i(e.useGeoJson,null)>-1:e.useGeoJson},on:{change:function(t){var n=e.useGeoJson,a=t.target,r=!!a.checked;if(Array.isArray(n)){var s=e._i(n,null);a.checked?s<0&&(e.useGeoJson=n.concat([null])):s>-1&&(e.useGeoJson=n.slice(0,s).concat(n.slice(s+1)))}else e.useGeoJson=r}}})]),e._v(" "),e.useGeoJson?n("textarea",{directives:[{name:"model",rawName:"v-model",value:e.pastedGeoJson,expression:"pastedGeoJson"}],attrs:{placeholder:"Paste a list of MultiPolygon coordinates, e.g. [[[[1, 1], [0, 0], [1, 0], [1, 1]]]]"},domProps:{value:e.pastedGeoJson},on:{input:function(t){t.target.composing||(e.pastedGeoJson=t.target.value)}}}):e._e(),e._v(" "),n("button",{staticClass:"btn btn-primary",on:{click:e.parseGeoJson}},[e._v("\n            Set\n        ")])]):e._e(),e._v(" "),"named_area"!==e.comparisonType?n("div",{attrs:{id:"mapdisplay"}}):e._e()])};T._withStripped=!0;var w=n(568),O=n.n(w);function k(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(e);t&&(a=a.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,a)}return n}function P(e){for(var t,n=1;n<arguments.length;n++)t=null==arguments[n]?{}:arguments[n],n%2?k(Object(t),!0).forEach((function(n){j(e,n,t[n])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(t)):k(Object(t)).forEach((function(n){Object.defineProperty(e,n,Object.getOwnPropertyDescriptor(t,n))}));return e}function j(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}var q={extends:m,name:"GeoEditor",data:function(){return{values:{point:{latitude:null,longitude:null,radius:0,radius_unit:"mi"},named_area:{country:null,marine:null,geography:null},custom_area:[[]]},geoCategory:null,leafletMap:null,markers:{point:{group:O.a.layerGroup(),circle:O.a.circle(),marker:O.a.marker()},named_area:{group:O.a.layerGroup(),data:null},custom_area:{group:O.a.layerGroup()}},pastedGeoJson:null,currentPolygon:[],useGeoJson:!1,mapInitialised:!1}},computed:P(P({},Object(s.e)(["schema"])),{},{radiusUnits:function(){return this.schema.raw.definitions.term.properties.geo_point.properties.radius_unit.enum},namedAreas:function(){return r.c().key((function(e){return e.key})).rollup((function(e){return e[0].value.enum})).object(r.a(this.schema.raw.definitions.term.properties.geo_named_area.properties))},radiusMeters:function(){return{mi:function(e){return e/62137e-8},yd:function(e){return e/1.0936},ft:function(e){return e/3.2808},in:function(e){return e/39.37},km:function(e){return 1e3*e},m:function(e){return e},cm:function(e){return e/100},mm:function(e){return e/1e3},nmi:function(e){return e/53996e-8}}[this.values.point.radius_unit](this.values.point.radius)}}),methods:{loadExisting:function(){var e=this;if(void 0!==this.existingTermId){var t=this.getFilterById(this.existingTermId);"custom_area"===this.comparisonType?(this.$set(this.values,"custom_area",t.content),this.values.custom_area.push([])):r.b(this.values[this.comparisonType]).forEach((function(n){e.$set(e.values[e.comparisonType],n,t.content[n]||null)})),"named_area"===this.comparisonType&&(this.geoCategory=r.b(t.content).filter((function(t){return r.b(e.namedAreas).includes(t)}))[0])}},setLatLng:function(e){if("point"===this.comparisonType&&(this.$set(this.values.point,"latitude",e.latlng.lat),this.$set(this.values.point,"longitude",e.latlng.lng)),"custom_area"===this.comparisonType){if(this.useGeoJson)return;var t=[e.latlng.lng,e.latlng.lat];0===this.currentPolygon.length?(this.currentPolygon.push(t),this.currentPolygon.push(t)):this.currentPolygon.splice(this.currentPolygon.length-1,0,t),this.$set(this.values.custom_area,this.values.custom_area.length-1,[this.currentPolygon])}},resetMap:function(){var e=this;r.d(this.markers).forEach((function(t){e.leafletMap.hasLayer(t.group)&&e.leafletMap.removeLayer(t.group)})),this.markers[this.comparisonType].group.addTo(this.leafletMap),this.leafletMap.on("click",this.setLatLng)},parseGeoJson:function(){if(null!==this.pastedGeoJson){var e=[],t=!0;try{e=JSON.parse(this.pastedGeoJson)}catch(e){t=!1,console.log("Invalid JSON.")}t&&this.$set(this.values,"custom_area",e)}},setGeoJson:function(){this.markers.custom_area.group.clearLayers();try{var e={type:"MultiPolygon",coordinates:this.values.custom_area};this.markers.custom_area.group.addLayer(O.a.geoJSON(e))}catch(e){console.log(e),this.markers.custom_area.group.addLayer(O.a.popup().setLatLng(this.leafletMap.getCenter()).setContent("Invalid GeoJSON."))}},addPolygon:function(){this.pastedGeoJson=null,this.currentPolygon=[],this.values.custom_area.push([])},deletePolygon:function(e){this.$delete(this.values.custom_area,e)},initMap:function(){this.leafletMap=O.a.map("mapdisplay"),this.leafletMap.setView([0,0],0),O.a.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",{maxZoom:18}).addTo(this.leafletMap),this.resetMap(),this.mapInitialised=!0}},mounted:function(){"named_area"!==this.comparisonType&&this.initMap()},watch:{comparisonType:function(){"named_area"===this.comparisonType||(this.mapInitialised?this.resetMap():setTimeout(this.initMap,1e3))},"values.point":{handler:function(){var e=[this.values.point.latitude,this.values.point.longitude];return e.some((function(e){return null===e||""===e}))?void this.markers.point.group.clearLayers():(this.leafletMap.setView(e),this.markers.point.marker.setLatLng(e),!this.markers.point.group.hasLayer(this.markers.point.marker)&&this.markers.point.group.addLayer(this.markers.point.marker),void(0<this.values.point.radius?(this.markers.point.circle.setLatLng(e),this.markers.point.circle.setRadius(this.radiusMeters),!this.markers.point.group.hasLayer(this.markers.point.circle)&&this.markers.point.group.addLayer(this.markers.point.circle)):this.markers.point.group.removeLayer(this.markers.point.circle)))},deep:!0},"values.named_area":{handler:function(e){var t=this,n=r.a(e);1<n.map((function(e){return null===e.value?0:1})).reduce((function(e,t){return e+t}))&&n.forEach((function(e){t.$set(t.values.named_area,e.key,null)}))},deep:!0},"values.custom_area":{handler:function(){this.pastedGeoJson=JSON.stringify(this.values.custom_area),this.setGeoJson()},deep:!0}}},C=(n(569),Object(d.a)(q,T,[function(){var e=this.$createElement,t=this._self._c||e;return t("small",[this._v("\n                Click on the map to add polygon points.\n                Try "),t("a",{attrs:{id:"geojson-link",href:"https://geojson.net"}},[this._v("geojson.net")]),this._v(" for editing\n                more complex MultiPolygon queries.\n            ")])}],!1,null,"0427c375",null));C.options.__file="src/components/editors/GeoEditor.vue";var N=C.exports,E=function(){var e=this.$createElement;return(this._self._c||e)("div",{staticClass:"flex-container flex-center"})};E._withStripped=!0;var $={extends:m,name:"OtherEditor",data:function(){return{values:{}}}},G=Object(d.a)($,E,[],!1,null,null,null);G.options.__file="src/components/editors/OtherEditor.vue";var J=G.exports;function I(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(e);t&&(a=a.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,a)}return n}function A(e){for(var t,n=1;n<arguments.length;n++)t=null==arguments[n]?{}:arguments[n],n%2?I(Object(t),!0).forEach((function(n){S(e,n,t[n])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(t)):I(Object(t)).forEach((function(n){Object.defineProperty(e,n,Object.getOwnPropertyDescriptor(t,n))}));return e}function S(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function L(e){return function(e){if(Array.isArray(e))return M(e)}(e)||function(e){if("undefined"!=typeof Symbol&&Symbol.iterator in Object(e))return Array.from(e)}(e)||function(e,t){if(e){if("string"==typeof e)return M(e,t);var n=Object.prototype.toString.call(e).slice(8,-1);return"Object"===n&&e.constructor&&(n=e.constructor.name),"Map"===n||"Set"===n?Array.from(e):"Arguments"===n||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)?M(e,t):void 0}}(e)||function(){throw new TypeError("Invalid attempt to spread non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()}function M(e,t){(null==t||t>e.length)&&(t=e.length);for(var n=0,a=Array(t);n<t;n++)a[n]=e[n];return a}var F={name:"TermEditor",components:{FieldPicker:n(232).a,string:g,number:x,geo:N,other:J},props:["existingTermId","parentId"],data:function(){var e={newFields:[],fieldType:"string",comparisonType:"equals",termName:null,queryValues:{},readableFieldTypes:{string:"Text",number:"Number",geo:"Geo",other:"Any"}};if(void 0!==this.existingTermId){var t=this.$store.getters["results/query/filters/getFilterById"](this.existingTermId);e.newFields=L(t.content.fields||[]),e.fieldType=t.key.includes("_")?t.key.split("_")[0]:"other",e.comparisonType=t.key.slice(t.key.indexOf("_")+1),e.termName=t.display.name}return e},computed:A(A(A(A({},Object(s.e)(["schema"])),Object(s.e)("results/query",["resourceIds"])),Object(s.c)("results/query/filters",["getFilterById"])),{},{terms:function(){var e=this.schema.terms[this.fieldType];return 1===e.length&&(""===e[0]||null===e[0])?[]:e},queryType:function(){return"other"===this.fieldType?this.comparisonType:[this.fieldType,this.comparisonType].join("_")},query:function(){var e={};return"geo"!==this.fieldType&&(e.fields=this.newFields),Array.isArray(this.queryValues)?e=this.queryValues:r.a(this.queryValues).forEach((function(t){null!==t.value&&(e[t.key]=t.value)})),e}}),methods:A(A(A({},Object(s.d)("results/query/filters",["changeKey","changeContent","changeName"])),Object(s.b)("results/query/filters",["addTerm"])),{},{setQueryValues:function(e){this.queryValues=e},addNewField:function(e){this.newFields.push(e)},deleteField:function(e){this.$delete(this.newFields,e)},closeDialog:function(){this.$parent.showEditor=!1},submitTerm:function(){void 0===this.existingTermId?this.addTerm({parent:this.parentId,key:this.queryType,content:this.query,display:{name:this.termName}}):(this.changeKey({key:this.queryType,id:this.existingTermId}),this.changeContent({content:this.query,id:this.existingTermId}),this.changeName({name:this.termName,id:this.existingTermId})),this.closeDialog()},resetQuery:function(){this.queryValues={}}}),watch:{fieldType:function(){this.resetQuery()},comparisonType:function(){this.resetQuery()}}},V=Object(d.a)(F,a,[],!1,null,null,null);V.options.__file="src/components/TermEditor.vue";t.default=V.exports}}]);