
    let abort_controller=null;
    // create progress bar 
    progress_dict={}
    const progress_of_merging=document.getElementById('progress-of-merging')
   // bar.animate(1.0);  // Number from 0.0 to 1.0
    // generate room name
    const channelId = Math.floor(Math.random() * 10000);
    // creating websocket connection  to recive downloading progress
    let websocket = new WebSocket(
      `ws://${window.location.host}/ws/${channelId}/`
      );
    websocket.onopen = function (e) {
      console.log("The connection was setup successfully !");
    };
    websocket.onclose = function (e) {
      console.log("Something unexpected happened !");
    };
    websocket.onerror = function(error) {
      console.error('WebSocket error:', error);
    };
    // waht is happen when recive message from server
    websocket.onmessage = function (e) {
      let data = JSON.parse(e.data);
      // redirect if an exception occure
      if (data.type === 'redirect') {
        window.location.href = data.url;
      }
      // update audio  or video progress bar
      if (data.type=='audio' || data.type=='video'){
        console.log(data.type)
        // create key of form 'aud-bar-${progress_id}' or 'vid-bar-${progress_id}'
        prog_elm_key=`${data.type.substr(0,3)}-bar-${data.progress_id}`
        update_progress_bar(prog_elm_key,data.progress)
        
      }
      // set state of merge 
      else{
        merge_status=document.getElementById(`merge-status-${data.progress_id}`)
        merge_status.innerHTML=data.type
        if (data.type=='merge-finished'){
          //get adaptive-form and pend it with 
          // merged filename to download it 
          const adaptive_form=document.getElementById('adaptive-form')
          const filename=document.getElementById('filename')
          filename.value=data.filename
          setTimeout(()=> {
            // remove progress section for finished operation
            document.getElementById(`${data.progress_id}`).remove()
            
          }, 500);
          console.log(data.filename)
          //make request to download file 
          adaptive_form.submit()
          
        }
      }
      
    };
    const url_form=document.getElementById("url-form")

    function update_progress_bar(prog_elm_key,progress) {
        //get progress bar element from progress bars dictionary 
        prog_element=progress_dict[prog_elm_key]
        prog_element.animate(progress)
        console.log(progress)
        if (progress==1){
          setTimeout(()=> {
            prog_element.destroy()
            document.getElementById(prog_elm_key).parentElement.remove();
          }, 300);
        }
    }
    function create_progress_bar(container_id){
      progress_bar = new ProgressBar.Line(`#${container_id}`, {
        strokeWidth: 4,
        easing: 'easeInOut',
        duration: 500,
        color: '#FFEA82',
        trailColor: '#eee',
        trailWidth: 1,
        svgStyle: {width: '100%', height: '100%'},
        text: {
          style: {
            // Text color.
            // Default: same as stroke color (options.color)
            color: '#999',
            position: 'absolute',
            left: '50%',
            top: '30px',
            padding: 0,
            margin: 0,
            transform:{
              prefix: true,
              value: 'translate(-50%, 0)'
          }
          },
          autoStyleContainer: false
        },
        from: {color: '#FFEA82'},
        to: {color: '#ED6A5A'},
        step: (state, bar) => {
          bar.setText(Math.round(bar.value()*100) + ' %');
          bar.path.setAttribute('stroke', state.color);  
        }
        });
      return progress_bar
    
    }
    url_form.addEventListener('submit', e => {
        // Prevent default submit to stop page reload
        e.preventDefault();
        //abort for previuos request
        if (abort_controller){
          abort_controller.abort();
        }
        // Create an new AbortController instance
        abort_controller = new AbortController();

        // Obtain a reference to the AbortSignal
        const signal = abort_controller.signal;
        // rest progress_of_merging section
        progress_of_merging.innerHTML=''
        // display wating... div
        const waiting_div=document.getElementById('waiting-div')
        waiting_div.classList.replace('d-none', 'd-block');
        
        // pending form with data
        const formData = new FormData(url_form);
        
        // make ajax request
        fetch('/', {
          method: 'POST',
          body: formData,
          signal:signal
        })
        .then(response => {
          console.log(' inside then 1')
          if (response.redirected) {
            const newUrl = response.url; // Get the redirected URL from the response
            console.log(`url is ${response.url}`)
            window.location.href = newUrl; // Redirect the user using window.location
          }
          else if (!response.ok) {
            waiting_div.classList.replace('d-block', 'd-none');
            throw new Error("Network response was not OK");
          }
          console.log(response.ok)
          return response.json()
          
        }).then(data=>{
          console.log(' inside then 2')
          // hide waiting sign
          waiting_div.classList.replace('d-block', 'd-none');
          info_div=document.getElementById('info-div')
          // reset info_div
          info_div.innerHTML=''
          // create childs
          // video image element
          img=document.createElement('img')
          img.src=data.video.thumbnail_url
          img.alt=data.video.title
          img.classList.add('col-6', 'rounded', 'mb-3');
          
          // video title element
          title=document.createElement('h5')
          title.innerHTML=`<span class="text-warning-emphasis">Title :</span>  ${data.video.title}`
          // video duration element
          duration=document.createElement('div')
          duration.innerHTML=`<span class="text-warning-emphasis">Duration :</span> ${data.video.duration}`
          
          // append  information childs 
          info_div.append(img)
          info_div.append(title)
          info_div.append(duration)
          
          
          
          options_table=document.getElementById('options-table')
          // reset table
          options_table.innerHTML=''
          // adding audio tr to table
          
          options_table.innerHTML+=`
            <tr>
              <td  class='text-warning'scope="col" colspan="3">Audio</td>
            </tr>`
          // adding audio options to table
          for (const s of data.audio_streams) {
            options_table.innerHTML+=`
              <tr>
                <td>${s.subtype}</td>
                <td>${s.size} MB</td>
                <td>
                  <form method="post" action="download/">
                    <input type="hidden" name="csrfmiddlewaretoken" value=${csrfToken}>
                    <button class="btn btn-outline-warning" name="url" value="${s.url}">download</button>
                    <input type="hidden" name="filename" value="${s.filename}">
                    <input type="hidden" name="mime_type" value="${s.mime_type}">
                  </form>
                </td>
              </tr>`
            
            
          }
          // adding video tr to table
          options_table.innerHTML+=`
            <tr>
              <td  class='text-warning'scope="col" colspan="3">Video</td>
            </tr>`
          
          // adding video options to table
          for (const s of data.video_streams) {
            tr=document.createElement('tr')
            // adding video subtype
            subtype_td=document.createElement('td')
            subtype_td.innerHTML=`${s.resolution} (${s.subtype})`
            tr.append(subtype_td)
            // adding video size
            size_td=document.createElement('td')
            size_td.innerHTML=`${s.size} MB`
            tr.append(size_td)
            // adding download section
            download_td=document.createElement('td')
            // if s.video_id ==> adaptive downlaod
            if ( s.video_id ) {
              btn=document.createElement('button')
              btn.innerHTML='download'
              btn.classList.add('btn','btn-outline-warning');
              // Add an onclick event listener
              btn.addEventListener('click', function() {
                  
                    if (websocket.readyState === WebSocket.OPEN) {
                    // create id for new progress section for each download operation
                    let progress_id = Math.floor(Math.random() * 10000);
                    aud_bar_container_id=`aud-bar-${progress_id}`
                    vid_bar_container_id=`vid-bar-${progress_id}`
                    
                    progress_of_merging.innerHTML +=`
                    <div class="text-center mt-3" id="${progress_id}">
                      <div class="row justify-content-center">
                        <div class="col-6 mb-5">
                          <div>Audio</div>
                          <div class="position-relative" id="${aud_bar_container_id}" style="height: 0.5rem" ></div>
                        </div>
                        <div class="col-6 mb-5">
                          <div>Video</div>
                          <div class="position-relative" id="${vid_bar_container_id}" style="height: 0.5rem" ></div>
                        </div>
                      </div>
                      <div  id='merge-status-${progress_id}'></div>
                      <hr>
                    </div>`
                    // send request to download file on server side and merge it
                    websocket.send(
                      JSON.stringify({
                         'video_id': s.video_id ,
                         'resolution':s.resolution,
                         'progress_id':progress_id
                        }));
                    // create progress bar for video 
                    video_bar=create_progress_bar(vid_bar_container_id)
                    audio_bar=create_progress_bar(aud_bar_container_id)
                    progress_dict[vid_bar_container_id] = video_bar;
                    progress_dict[aud_bar_container_id] = audio_bar;
                  } 
                  else {
                      console.error('WebSocket is not open. ReadyState:', websocket.readyState);
                  }
                  });
              download_td.append(btn)
  
            }
            else{
              form=document.createElement('form')
              form.method='post'
              form.action='download/'
              const csrfTokenInput = document.createElement('input');
              csrfTokenInput.type = 'hidden';  
              csrfTokenInput.name = 'csrfmiddlewaretoken';
              csrfTokenInput.value = '{{ csrf_token }}'; 
              form.append(csrfTokenInput)
              btn=document.createElement('button')
              btn.innerHTML='download'
              btn.name='url'
              btn.value=s.url
              btn.classList.add('btn','btn-outline-warning');
              form.append(btn)
              filename=document.createElement('input')
              filename.type='hidden'
              filename.name='filename'
              filename.value=s.filename
              form.append(filename)
              mime_type=document.createElement('input')
              mime_type.type='hidden'
              mime_type.name='mime_type'
              mime_type.value=s.mime_type
              form.append(mime_type)
              download_td.append(form)
            }
            tbody=document.createElement('tbody')
            tr.append(download_td)
            tbody.append(tr)
            options_table.append(tbody)
            
            
          }
       
          })  
          .catch(error => {
            if (error.name === 'AbortError') {
              console.log('abbort error')
            } else {
              console.log("Error:", error);
            }
          }).finally(() => {
            // Cleanup logic
          });
          
        });

