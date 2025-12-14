const e = React.createElement
function App(){
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
    fetch('/api/upload',{method:'POST',body:fd}).then(r=>r.json()).then(()=>{fetch('/api/images').then(r=>r.json()).then(setImages)})
  }

  function login(ev){
    ev.preventDefault()
    const form=new FormData(ev.target)
    const body={email:form.get('email'),password:form.get('password')}
    fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}).then(r=>r.json()).then(d=>{if(!d.error) setUser(d)})
  }

  return e('div',null,
    e('header',null,e('h1',null,'BHV'),user?e('div',null,user.email+' | ',e('button',{onClick:logout},'Logout')):e('div',null,e('a',{href:'#login'},'Login'))),
    e('main',null,
      user?e('section',null,e('form',{onSubmit:submitUpload},
        e('input',{type:'file',onChange:(ev)=>setFile(ev.target.files[0])}),
        e('textarea',{placeholder:'Narrative',value:narrative,onChange:(ev)=>setNarrative(ev.target.value)}),
        e('button',{type:'submit'},'Upload')
      )):null,
      e('section',{className:'gallery'},images.map(img=>e('article',{key:img.id},e('a',{href:img.url},e('img',{src:img.thumb})),e('p',null,img.narrative))))
    ),
    e('div',{id:'login'},e('h3',null,'Login'),e('form',{onSubmit:login},e('input',{name:'email',placeholder:'email'}),e('input',{name:'password',type:'password',placeholder:'password'}),e('button',null,'Login')))
  )
}

ReactDOM.createRoot(document.getElementById('root')).render(e(App))
