import mitt from 'mitt';

const events = {
  recordsRetrieved: 'RECORDS_RETRIEVED',
  querySet: 'QUERY_SET',
};

const emitter = mitt();
// polyfill for .once() handler from https://github.com/developit/mitt/issues/136
emitter.once = function (type, handler) {
  const fn = (...args) => {
    emitter.off(type, fn);
    handler(args);
  };
  emitter.on(type, fn);
  handler._ = fn;
};

export { events, emitter };
