// prevent console usage from throwing errors if there is no console
!function(global, noop, prop){
  'console' in global || (global.console = {});

  var methods = [ 'assert', 'count', 'debug', 'dir', 'dirxml', 'error', 'exception',
                  'group', 'groupCollapsed', 'groupEnd', 'info', 'log', 'markTimeline',
                  'profile', 'profileEnd', 'time', 'timeEnd', 'trace', 'warn' ];

  while (prop = methods.shift()) {
    prop in console || (console[prop] = noop);
  }
}(new Function('return this')(), function(){});