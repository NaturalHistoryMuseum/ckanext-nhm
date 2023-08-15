import axios from 'axios';

const api = axios.create({
  baseURL: '/api/3/action/',
  timeout: 20000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export function post(action, body) {
  return api.post(action, body).then((response) => {
    return response.data;
  });
}

export function get(action) {
  return api.get(action).then((response) => {
    return response.data;
  });
}

export function camelCase(str) {
  return str
    .split(/[^A-Za-z0-9]+/g)
    .filter((s) => s !== '')
    .map((s, i) => {
      s = s.toLowerCase();
      if (i > 0) {
        s = s[0].toUpperCase() + s.slice(1);
      }
      return s;
    })
    .join('');
}

export class AbortError extends Error {
  constructor(jobId) {
    super(`Aborted ${jobId}`);
    this.name = 'AbortError';
  }
}
