import axios from 'axios';
import rateLimit from 'axios-rate-limit';

const api = rateLimit(
  axios.create({
    baseURL: '/api/3/action/',
    timeout: 20000,
    headers: {
      'Content-Type': 'application/json',
    },
  }),
  { maxRPS: 5 },
);

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
