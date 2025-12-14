import React from 'react'

export default function App(){
  const [user,setUser]=React.useState(null)
  const [images,setImages]=React.useState([])
  const [file,setFile]=React.useState(null)
  const [narrative,setNarrative]=React.useState('')

  React.useEffect(()=>{fetch('/api/images').then(r=>r.json()).then(setImages)},[])

  function logout(){fetch('/api/logout',{method:'POST'}).then(()=>setUser(null))}

  function submitUpload(ev){
    ev.preventDefault()
    if(!file) return
    const fd=new FormData()
    fd.append('file',file)
    fd.append('narrative',narrative)
    fetch('/api/upload',{method:'POST',body:fd}).then(()=>{fetch('/api/images').then(r=>r.json()).then(setImages)})
  }

  function login(ev){
    ev.preventDefault()
    const form=new FormData(ev.target)
    const body={email:form.get('email'),password:form.get('password')}
    fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}).then(r=>r.json()).then(d=>{if(!d.error) setUser(d)})
  }

  return (
    React.createElement('div',null,
      React.createElement('header',null,
        React.createElement('h1',null,'Behavioral Health Vault'),
        user?React.createElement('div',null,user.email,' ',React.createElement('button',{onClick:logout,style:{marginLeft:8}},'Logout')):React.createElement('div',null)
      ),
      React.createElement('div',{className:'container'},
        React.createElement('section',{className:'form'},
          React.createElement('h3',null,'Upload'),
          user?React.createElement('form',{onSubmit:submitUpload},
            React.createElement('input',{type:'file',onChange:(ev)=>setFile(ev.target.files[0])}),
            React.createElement('textarea',{placeholder:'Narrative',value:narrative,onChange:(ev)=>setNarrative(ev.target.value)}),
            React.createElement('div',null,React.createElement('button',{type:'submit'},'Upload'))
          ):React.createElement('div',null,'Login to upload')
        ),
        React.createElement('section',{style:{marginTop:20}},
          React.createElement('h3',null,'Gallery'),
          React.createElement('div',{className:'gallery'},images.map(img=>React.createElement('article',{key:img.id,className:'card'},React.createElement('a',{href:img.url},React.createElement('img',{src:img.thumb})),React.createElement('p',null,img.narrative))))
        ),
        React.createElement('section',{style:{marginTop:20}},
          React.createElement('h3',null,'Login'),
          React.createElement('form',{onSubmit:login, className:'form'},
            React.createElement('input',{name:'email',placeholder:'Email',type:'email'}),
            React.createElement('input',{name:'password',type:'password',placeholder:'Password'}),
            React.createElement('div',null,React.createElement('button',null,'Login'))
          )
        )
      )
    )
  )
}
