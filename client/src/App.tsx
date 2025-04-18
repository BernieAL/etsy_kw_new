import { useState } from 'react'

function App() {
  
  const [storeUrls, setStoreUrls] = useState<string[]>([''])
  const [loading, setLoading] = useState(false)
  const [reportUrl, setReportUrl] = useState<string | null>(null)

  const handleChange = (index: number, value: string) => {
    const updated = [...storeUrls]
    updated[index] = value
    setStoreUrls(updated)
  }

  const addField = () => setStoreUrls([...storeUrls, ''])

  const handleSubmit = async () => {
    setLoading(true)
    const response = await fetch('http://localhost:5000/api/scrape', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ urls: storeUrls }),
    })

    const data = await response.json()
    setReportUrl(data.download_url)
    setLoading(false)
  }

  return (
    <div style={{ padding: '2rem' }}>
      <h1>Etsy Keyword Analyzer</h1>
      {storeUrls.map((url, i) => (
        <input
          key={i}
          value={url}
          placeholder="Paste Etsy listing URL"
          onChange={(e) => handleChange(i, e.target.value)}
          style={{ display: 'block', marginBottom: '0.5rem', width: '100%' }}
        />
      ))}
      <button onClick={addField}>+ Add another</button>
      <br />
      <button onClick={handleSubmit} disabled={loading}>
        {loading ? 'Analyzing...' : 'Submit'}
      </button>
      {reportUrl && (
        <p>
          Report Ready: <a href={reportUrl}>Download CSV</a>
        </p>
      )}
    </div>
  )
}

export default App
