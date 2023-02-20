import axios from 'axios';
import { parse as parseJSON } from 'json-bigint';

// this is the base query used for all API search calls, it excludes any record that doesn't have
// an image field
const baseQuery = {
  filters: {
    and: [
      {
        // the Image field must exist
        exists: {
          fields: ['Image'],
        },
      },
      {
        // the Image field must not have the empty string as the value
        not: [
          {
            string_equals: {
              fields: ['Image'],
              value: '',
            },
          },
        ],
      },
    ],
  },
};

/**
 * A class that assists with using the Data Portal's API, specifically the multisearch API.
 */
export class API {
  /**
   * @param state the store's state
   */
  constructor(state) {
    this.state = state;
    this.api = axios.create({
      baseURL: '/api/3/action/',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  /**
   * Calls an API action using a POST request with the body as a JSON payload.
   *
   * @param action the action to call
   * @param body the object body that will be sent with the POST request as JSON
   * @returns {Promise<Object>} the response JSON
   */
  async post(action, body) {
    // transformResponse stops axios parsing the json response automatically so that we can
    const response = await this.api.post(action, body, {
      transformResponse: [(data) => data],
    });
    // use JSONbig to make sure we parse any enormous ints correctly
    return parseJSON(response.data);
  }

  /**
   * Calls an API action using a GET request.
   *
   * @param action the action to call
   * @returns {Promise<Object>} the response JSON
   */
  async get(action) {
    // transformResponse stops axios parsing the json response automatically so that we can
    const response = await this.api.get(action, {
      transformResponse: [(data) => data],
    });
    // use JSONbig to make sure we parse any enormous ints correctly
    return parseJSON(response.data);
  }

  /**
   * Utility function used to build a search body Object. The baseQuery will always be included
   * but the current store state's query is optionally included. The resulting Object can be
   * POSTed directly to the multisearch endpoint and used as a base for many of the related
   * endpoints too.
   *
   * @param size the size of the response to request (i.e. number of hits), defaults to 15
   * @param use_query whether to use the store state's query or not, defaults to true
   * @returns {{size: number, query: Object, resource_ids: (string)[]}} the body Object
   */
  getSearchBody(size = 15, use_query = true) {
    // make a copy of the baseQuery
    const query = JSON.parse(JSON.stringify(baseQuery));
    // only add the store state's query if it's asked for and defined
    if (use_query && Object.keys(this.state.query).length > 0) {
      // add the current query
      query.filters.and.push(this.state.query);
    }
    return {
      resource_ids: [this.state.resourceId],
      query: query,
      size: size,
    };
  }

  /**
   * Asynchronous iterator of records from the multisearch API. Records are retrieved in chunks
   * and then yielded to the caller seamlessly, giving the appearance of a single stream when in
   * fact multiple calls are made repeatedly to retrieve the next set of records when required.
   *
   * @param size the number of records to request at a time, default: 100
   * @param use_query whether to use the store state's query or not, default: true
   * @returns {AsyncGenerator<*, void, *>} yields record Objects, note that this is the root
   *                                       level record from the response so the actual data is
   *                                       available at ".data".
   */
  async *getRecords(size = 100, use_query = true) {
    let body = this.getSearchBody(size, use_query);
    while (true) {
      const json = await this.post('datastore_multisearch', body);
      yield* json.result.records;
      if (!json.result.after) {
        break;
      } else {
        body.after = json.result.after;
      }
    }
  }

  /**
   * Asynchronous function which calls the multisearch API to retrieve the total number of records
   * that match the given search.
   *
   * @param use_query whether to use the store state's query or not, default: true
   * @returns {Promise<Number>} the total number of matching records
   */
  async getRecordCount(use_query = true) {
    const body = this.getSearchBody(0, use_query);
    const json = await this.post('datastore_multisearch', body);
    return json.result.total;
  }

  /**
   * Asynchronous iterator of values from the multisearch value autocomplete API. Values are
   * retrieved in chunks and then yielded to the caller seamlessly, giving the appearance of a
   * single stream when in fact multiple calls are made repeatedly to retrieve the next set of
   * values when required.
   *
   * @param field the field to autocomplete on
   * @param prefix the prefix search to perform, can be the empty string
   * @param size the number of values to request at a time, default: 10
   * @param use_query whether to use the store state's query, default: true
   * @returns {AsyncGenerator<*, void, *>} yields string values in alphabetical order
   */
  async *autocomplete(field, prefix, size = 10, use_query = true) {
    let body = this.getSearchBody(size, use_query);
    body.field = field;
    body.prefix = prefix;
    while (true) {
      const json = await this.post('datastore_value_autocomplete', body);
      if (json.result.values.length > 0) {
        yield* json.result.values;
        body.after = json.result.after;
      } else {
        break;
      }
    }
  }
}
