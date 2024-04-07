const url = 'https://feishu.soufe.cn/ip/batch';
const short_url_api = '/api/shorten_urls';


export const translate = async (sourceValueList: Array<any>) => {
  return await fetch(short_url_api, {
    method: 'POST',
    body: JSON.stringify({
      field_value_list: sourceValueList
    }),
    headers: { 'Content-Type': 'application/json' }
  })
    .then(res => res.json())
    .then(json => { return json })
    .catch(err => console.error('error:' + err));
};
