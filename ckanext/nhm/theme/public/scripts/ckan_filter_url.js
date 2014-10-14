/**
 * CKanFilterUrl
 *
 * Class used to parse and create URLs with a query string parameter 'filter' build as 'name:value|....'
 *
 * TODO: This should be moved in a helper library, as the same code is used in the map plugin.
 */
this.CkanFilterUrl = function(input_url){
  /**
   * initialize
   *
   * Set up the object
   */
  this.initialize = function(){
    if (typeof input_url !== 'undefined'){
      this.set_url(input_url);
    } else {
      this.base = '';
      this.qs = {};
    }
  };

  /**
   * set_url
   *
   * Set this object's URL
   */
  this.set_url = function(url){
    var parts = url.split('?');
    this.base = parts[0];
    this.qs = {};
    if (parts.length > 1){
      var qs_idx = parts[1].split('&');
      for (var i in qs_idx){
        var p = qs_idx[i].split('=');
        p[0] = decodeURIComponent(p[0]);
        p[1] = decodeURIComponent(p[1]);
        this.qs[p[0]] = p[1]
      }
      if (typeof this.qs['filters'] !== 'undefined'){
        this.set_filters(this.qs['filters']);
      }
    }

    return this;
  };

  /**
   * add_filter
   *
   * Add a filter to the current URL.
   */
  this.add_filter = function(name, value){
    if (typeof this.qs['filters'] === 'undefined'){
      this.qs['filters'] = {};
    }
    if ($.isArray(value)){
      // TODO: check how ckan handles multivalued.
      this.qs['filters'][name] = value.join('');
    } else {
      this.qs['filters'][name] = value;
    }

    return this;
  };

  /**
   * remove_filter
   *
   * Remove filter from the current url
   */
  this.remove_filter = function(name){
    if (typeof this.qs['filters'] !== 'undefined'){
      delete this.qs['filters'][name];
      if ($.isEmptyObject(this.qs['filters'])){
        delete this.qs['filters'];
      }
    }
    return this;
  };

  /**
   * set_filter
   *
   * Set a filter value on the URL. If the value evaluates to false, the filter is removed
   */
  this.set_filter = function(name, value){
    if (!value){
      this.remove_filter(name);
    } else {
      this.add_filter(name, value);
    }

    return this;
  };

  /**
   * set_filters
   *
   * Set the filters of the URL. The value may be a decoded query string formated filter (a:b|...), or a dictionary
   * of name to value.
   */
  this.set_filters = function(filters){
    delete this.qs['filters'];
    if (typeof filters == 'string' && filters){
      var split = filters.split('|');
      for (var i in split){
        var parts = split[i].split(':');
        if (parts.length == 2){
          this.set_filter(parts[0], parts[1])
        }
      }
    } else if (typeof filters == 'object'){
      for (var i in filters){
        this.set_filter(i, filters[i])
      }
    }
    return this;
  };

  /**
   * get_filters
   *
   * Returns the filter query string alone (not encoded)
   */
  this.get_filters = function(){
    if (typeof this.qs['filters'] === 'undefined'){
      return '';
    }
    var b_filter = [];
    for (var f in this.qs['filters']){
      b_filter.push(f + ':' + this.qs['filters'][f])
    }
    return b_filter.join('|')
  };

  /**
   * get_filter
   *
   * Return the value of a single filter in the filter query string
   */
  this.get_filter = function(name){
    if (!this.qs['filters'] || !this.qs['filters'][name]){
      return '';
    }
    return this.qs['filters'][name];
  };

  /**
   * get_url
   *
   * Return the URL as a string
   */
  this.get_url = function(){
    var b_qs = [];
    for (var i in this.qs){
      var val;
      if (i == 'filters'){
        val = this.get_filters();
      } else {
        val = this.qs[i];
      }
      b_qs.push(encodeURIComponent(i) + '=' + encodeURIComponent(val));
    }

    return this.base + '?' + b_qs.join('&');
  };

  this.initialize();
};