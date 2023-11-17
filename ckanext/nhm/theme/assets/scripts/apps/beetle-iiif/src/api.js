import axios from 'axios';
import { parse as parseJSON } from 'json-bigint';

/**
 * A class that assists with using the Data Portal's API, specifically the multisearch API.
 */
export class API {
  constructor() {
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
   * Asynchronous iterator of records from the multisearch API. Records are retrieved in chunks
   * and then yielded to the caller seamlessly, giving the appearance of a single stream when in
   * fact multiple calls are made repeatedly to retrieve the next set of records when required.
   *
   * @param body the request body (resource ids, query, and size)
   * @returns {AsyncGenerator<*, void, *>} yields record Objects, note that this is the root
   *                                       level record from the response so the actual data is
   *                                       available at ".data".
   */
  async *getRecords(body) {
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
   * @param body the request body (resource ids and query - size will be overridden)
   * @returns {Promise<Number>} the total number of matching records
   */
  async getRecordCount(body) {
    body.size = 0;
    const json = await this.post('datastore_multisearch', body);
    return json.result.total;
  }

  /**
   * Asynchronous iterator of values from the multisearch value autocomplete API. Values are
   * retrieved in chunks and then yielded to the caller seamlessly, giving the appearance of a
   * single stream when in fact multiple calls are made repeatedly to retrieve the next set of
   * values when required.
   *
   * @param body the request body (resource ids, query, and size)
   * @param field the field to autocomplete on
   * @param prefix the prefix search to perform, can be an empty string
   * @returns {AsyncGenerator<*, void, *>} yields string values in alphabetical order
   */
  async *autocomplete(body, field, prefix = '') {
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

export default new API();
