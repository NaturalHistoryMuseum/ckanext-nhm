export function post(action, body) {
    return fetch('/api/3/action/' + action, {
        method:      'POST',
        mode:        'cors',
        cache:       'no-cache',
        credentials: 'same-origin',
        headers:     {
            'Content-Type': 'application/json'
        },
        redirect:    'follow',
        referrer:    'no-referrer',
        body:        JSON.stringify(body)
    }).then(response => {
        return response.json();
    });
}

export function get(action) {
    return fetch('/api/3/action/' + action, {
        method: 'GET'
    }).then(response => {
        return response.json();
    })
}

export function camelCase(str) {
    return str.split(/[^A-Za-z0-9]+/g).filter(s => s !== '').map((s, i) => {
        s = s.toLowerCase();
        if (i > 0) {
            s = s[0].toUpperCase() + s.slice(1);
        }
        return s;
    }).join('')
}