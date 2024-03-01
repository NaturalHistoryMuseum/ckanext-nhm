import axios from 'axios';

const api = axios.create({
  baseURL: '/api/3/action/',
  timeout: 20000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export async function post(action, body) {
  return api.post(action, body).then((response) => {
    return response.data;
  });
}

export async function get(action, params = {}) {
  return api.get(action, { params }).then((response) => {
    return response.data;
  });
}

export async function* multisearch(body) {
  while (true) {
    const json = await post('datastore_multisearch', body);
    yield* json.result.records;
    if (!json.result.after) {
      break;
    } else {
      body.after = json.result.after;
    }
  }
}
