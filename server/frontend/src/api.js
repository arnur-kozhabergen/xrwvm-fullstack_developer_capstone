export async function api(url, options = {}) {
  if (options.method && options.method !== 'GET') {
    await fetch('/djangoapp/session', {credentials:'same-origin'});
    const token = document.cookie.split('; ').find(v => v.startsWith('csrftoken='))?.split('=').slice(1).join('=');
    options.headers = {...options.headers, 'X-CSRFToken': decodeURIComponent(token || '')};
  }
  const response = await fetch(url, {credentials:'same-origin', ...options});
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || 'The request could not be completed.');
  return data;
}
export function post(url, data) {
  return api(url, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data)});
}
