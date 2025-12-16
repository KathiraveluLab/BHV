import React from 'react'

export default function App(){
  const [user,setUser]=React.useState(null)
  const [images,setImages]=React.useState([])
  const [file,setFile]=React.useState(null)
  const [narrative,setNarrative]=React.useState('')
  const [error,setError]=React.useState('')

  React.useEffect(()=>{
    fetch('/api/images')
      .then(r=>r.json())
      .then(setImages)
      .catch(err=>{
        console.error('Failed to load images:', err)
        setError('Failed to load images')
      })
  },[])

  function logout(){
    fetch('/api/logout',{method:'POST'})
      .then(()=>setUser(null))
      .catch(err=>{
        console.error('Logout failed:', err)
        setError('Logout failed')
      })
  }

  function submitUpload(ev){
    ev.preventDefault()
    if(!file){
      setError('Please select a file')
      return
    }
    setError('')
    const fd=new FormData()
    fd.append('file',file)
    fd.append('narrative',narrative)
    fetch('/api/upload',{method:'POST',body:fd})
      .then(r=>{
        if(!r.ok) throw new Error('Upload failed')
        return r.json()
      })
      .then(d=>{
        setFile(null)
        setNarrative('')
        return fetch('/api/images').then(r=>r.json()).then(setImages)
      })
      .catch(err=>{
        console.error('Upload failed:', err)
        setError('Upload failed: '+err.message)
      })
  }

  function login(ev){
    ev.preventDefault()
    setError('')
    const form=new FormData(ev.target)
    const body={email:form.get('email'),password:form.get('password')}
    fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)})
      .then(r=>{
        if(!r.ok){
          if(r.status===401) throw new Error('Invalid email or password')
          throw new Error('Login failed')
        }
        return r.json()
      })
      .then(d=>{
        if(d.error){
          setError(d.error)
        } else {
          setUser(d)
          ev.target.reset()
        }
      })
      .catch(err=>{
        console.error('Login error:', err)
        setError(err.message)
      })
  }

  return (
    <div>
      <header>
        <h1>Behavioral Health Vault</h1>
        {user ? (
          <div>
            {user.email}
            <button onClick={logout} style={{marginLeft: 8}}>Logout</button>
          </div>
        ) : (
          <div></div>
        )}
      </header>
      {error && (
        <div style={{color: 'red', padding: '10px', backgroundColor: '#ffe0e0', margin: '10px'}}>
          {error}
        </div>
      )}
      <div className='container'>
        <section className='form'>
          <h3>Upload</h3>
          {user ? (
            <form onSubmit={submitUpload}>
              <input type='file' onChange={(ev)=>setFile(ev.target.files[0])} />
              <textarea placeholder='Narrative' value={narrative} onChange={(ev)=>setNarrative(ev.target.value)} />
              <div>
                <button type='submit'>Upload</button>
              </div>
            </form>
          ) : (
            <div>Login to upload</div>
          )}
        </section>
        <section style={{marginTop: 20}}>
          <h3>Gallery</h3>
          <div className='gallery'>
            {images.map(img => (
              <article key={img.id} className='card'>
                <a href={img.url}>
                  <img src={img.thumb} />
                </a>
                <p>{img.narrative}</p>
              </article>
            ))}
          </div>
        </section>
        <section style={{marginTop: 20}}>
          <h3>Login</h3>
          <form onSubmit={login} className='form'>
            <input name='email' placeholder='Email' type='email' />
            <input name='password' type='password' placeholder='Password' />
            <div>
              <button>Login</button>
            </div>
          </form>
        </section>
      </div>
    </div>
  )
}
