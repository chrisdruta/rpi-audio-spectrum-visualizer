(this["webpackJsonpreact-web-app"]=this["webpackJsonpreact-web-app"]||[]).push([[0],{118:function(e,t,n){},119:function(e,t,n){},179:function(e,t,n){"use strict";n.r(t);var a=n(24),r=n(0),c=n.n(r),o=n(14),s=n.n(o),i=(n(118),n(84)),h=n(85),l=n(111),u=n(108),d=(n(119),n(182)),j=n(181),f=n(76),p=n(183),b=n(86),O=n.n(b),g=function(e){Object(l.a)(n,e);var t=Object(u.a)(n);function n(){var e;Object(i.a)(this,n);for(var a=arguments.length,r=new Array(a),c=0;c<a;c++)r[c]=arguments[c];return(e=t.call.apply(t,[this].concat(r))).state={statusData:"",cavaConfig:{bruh:"bruh"}},e.host="http://192.168.1.12:5000/controller",e.handleRefreshStatus=function(){fetch(e.host).then((function(e){return e.json()})).then((function(t){return e.setState({statusData:JSON.stringify(t,null,4)})})).catch((function(e){return alert(e)}))},e.handleChangeMode=function(t){fetch("".concat(e.host,"/mode/").concat(t),{method:"PUT"}).then((function(t){202!==t.status?alert("Change mode failed."):e.handleRefreshStatus()})).catch((function(e){return alert(e)}))},e}return Object(h.a)(n,[{key:"render",value:function(){var e=this;return Object(a.jsxs)("div",{className:"App",children:[Object(a.jsx)(d.a.Title,{children:"rpi-controller"}),Object(a.jsxs)("div",{className:"Flex-container",children:[Object(a.jsxs)(j.a,{title:"Status",style:{width:500,height:270},children:[Object(a.jsx)(f.a,{type:"primary",onClick:this.handleRefreshStatus,children:"Refresh Status"}),Object(a.jsx)("p",{}),Object(a.jsx)(p.a.TextArea,{disabled:!0,value:this.state.statusData,rows:5,style:{resize:"none"}})]}),Object(a.jsxs)(j.a,{title:"Control",style:{width:500},children:[Object(a.jsx)(f.a,{type:"primary",onClick:function(){return e.handleChangeMode("idle")},children:"Change Mode Idle"}),Object(a.jsx)("p",{}),Object(a.jsx)(f.a,{type:"primary",onClick:function(){return e.handleChangeMode("pink")},children:"Change Mode Pink"}),Object(a.jsx)("p",{}),Object(a.jsx)(f.a,{type:"primary",onClick:function(){return e.handleChangeMode("cava")},children:"Change Mode Cava"}),Object(a.jsx)("p",{}),Object(a.jsx)(d.a.Paragraph,{strong:!0,children:"Cava Config"}),Object(a.jsx)(O.a,{src:this.state.cavaConfig,onEdit:function(e){return!0},displayDataTypes:!1,name:null,theme:"ocean",style:{textAlign:"left"}})]})]})]})}}]),n}(c.a.Component);Boolean("localhost"===window.location.hostname||"[::1]"===window.location.hostname||window.location.hostname.match(/^127(?:\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}$/));s.a.render(Object(a.jsx)(c.a.StrictMode,{children:Object(a.jsx)(g,{})}),document.getElementById("root")),"serviceWorker"in navigator&&navigator.serviceWorker.ready.then((function(e){e.unregister()})).catch((function(e){console.error(e.message)}))}},[[179,1,2]]]);
//# sourceMappingURL=main.c832f351.chunk.js.map