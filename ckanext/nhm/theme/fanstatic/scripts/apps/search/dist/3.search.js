(window.webpackJsonpsearch=window.webpackJsonpsearch||[]).push([[3],{508:function(e,r,t){"use strict";t.r(r);var s=function(){var e=this,r=e.$createElement,t=e._self._c||r;return t("div",{staticClass:"fields resourceid-list floating flex-container flex-column flex-left"},[t("div",[t("input",{directives:[{name:"model",rawName:"v-model",value:e.allResourcesToggle,expression:"allResourcesToggle"}],attrs:{type:"checkbox",id:"toggleAll"},domProps:{checked:Array.isArray(e.allResourcesToggle)?e._i(e.allResourcesToggle,null)>-1:e.allResourcesToggle},on:{change:[function(r){var t=e.allResourcesToggle,s=r.target,c=!!s.checked;if(Array.isArray(t)){var o=e._i(t,null);s.checked?o<0&&(e.allResourcesToggle=t.concat([null])):o>-1&&(e.allResourcesToggle=t.slice(0,o).concat(t.slice(o+1)))}else e.allResourcesToggle=c},e.toggleAllResourceSelect]}}),e._v(" "),t("label",{attrs:{for:"toggleAll"}},[e._v("Select all")])]),e._v(" "),e._l(e.packageList,(function(r,s){return t("span",{key:r.id},[t("a",{attrs:{href:"#",id:r.id,value:r.id},on:{click:function(r){return e.togglePackageResources(s)}}},[e._v(e._s(r.name))]),e._v(" "),t("div",{staticClass:"fields"},e._l(r.resources,(function(r){return t("span",{key:r.id},[t("input",{directives:[{name:"model",rawName:"v-model",value:e.resourceIds,expression:"resourceIds"}],attrs:{type:"checkbox",id:r.id},domProps:{value:r.id,checked:Array.isArray(e.resourceIds)?e._i(e.resourceIds,r.id)>-1:e.resourceIds},on:{change:function(t){var s=e.resourceIds,c=t.target,o=!!c.checked;if(Array.isArray(s)){var l=r.id,n=e._i(s,l);c.checked?n<0&&(e.resourceIds=s.concat([l])):n>-1&&(e.resourceIds=s.slice(0,n).concat(s.slice(n+1)))}else e.resourceIds=o}}}),e._v(" "),t("label",{attrs:{for:r.id}},[e._v(e._s(r.name))])])})),0)])}))],2)};s._withStripped=!0;var c=t(6);function o(e,r){var t=Object.keys(e);if(Object.getOwnPropertySymbols){var s=Object.getOwnPropertySymbols(e);r&&(s=s.filter((function(r){return Object.getOwnPropertyDescriptor(e,r).enumerable}))),t.push.apply(t,s)}return t}function l(e){for(var r,t=1;t<arguments.length;t++)r=null==arguments[t]?{}:arguments[t],t%2?o(Object(r),!0).forEach((function(t){n(e,t,r[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(r)):o(Object(r)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(r,t))}));return e}function n(e,r,t){return r in e?Object.defineProperty(e,r,{value:t,enumerable:!0,configurable:!0,writable:!0}):e[r]=t,e}var a={name:"ResourceList",data:function(){return{allResourcesToggle:!1}},computed:l({},Object(c.e)(["resourceIds"]),{},Object(c.e)("constants",["packageList"]),{resourceIds:{get:function(){return this.$store.state.resourceIds},set:function(e){this.$store.commit("setResourceIds",e)}}}),methods:l({},Object(c.d)(["togglePackageResources"]),{toggleAllResourceSelect:function(e){e.target.checked?this.$store.commit("selectAllResources"):this.resourceIds=[]}}),watch:{resourceIds:function(e,r){e.length<r.length&&(this.allResourcesToggle=!1)}}},i=t(3),u=Object(i.a)(a,s,[],!1,null,null,null);u.options.__file="src/components/ResourceList.vue";r.default=u.exports}}]);