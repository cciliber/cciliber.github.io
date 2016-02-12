
window.onload = function onload_window() {

    'use strict';

    
    var timeModalRadius = 300;
    var timeModalOpacity = 300;
    var timeModalFlying = 300;
    
    
    
    var color_project = {
      structure: '#63B6B1',
      icubworld: '#CE534C',
      multisensory: '#285DAE'
    };
    
    var proj_structure = init_project('structure');
    var proj_icubworld = init_project('icubworld');
    var proj_multisensory = init_project('multisensory');

    var navigator = document.getElementById('navigator');
    
    var research_modal_container = document.getElementsByClassName('research-modal-container')[0];

    var research_projects = [proj_structure,proj_icubworld,proj_multisensory];
    
    var flying_modal = document.getElementsByClassName('flying-modal')[0];

    
    
    var basicBackgroundColor = getColorOfElement(document.getElementsByTagName('a')[0]);
    
    
    function init_project(project_name) {
        
//        var modal = document.getElementsByClassName('research-modal _project-' + project_name)[0];
        var modal = document.getElementsByClassName('sec _project-' + project_name)[0];
        
        var button_close_modal = modal.getElementsByClassName('_close')[0];

        var project  = document.getElementsByClassName('research-project _project-' + project_name)[0];

        var flying  = document.getElementsByClassName('flying moving _project-' + project_name)[0];

        var dummy  = document.getElementsByClassName('flying dummy _project-' + project_name)[0];

        var modal_base = document.getElementsByClassName('flying-modal')[0];

        var button_open_modal = project.getElementsByClassName('clickable')[0];
                
        var color = color_project[project_name];
        
        
        var openModal = openResearchModal(project_name);
        var switchModal = switchResearchModal(project_name);
        var closeModal = closeResearchModal(project_name);
        
        button_open_modal.addEventListener('click', openModal);
        dummy.addEventListener('click', switchModal);
        button_close_modal.addEventListener('click',closeModal);
        
        
        
        var project_object = {
            
            active: false,
            name: project_name,
            color: color,
            
            modal: modal,
            modal_base: modal_base,
            
            button_open_modal: button_open_modal,
            button_close_modal: button_close_modal,
            
            dummy : dummy,
            
            
            openModal : openModal,
            switchModal : switchModal,
            closeModal : closeModal,
            
            flying: flying
        };
        
        
        
        
        //set the color of the back
        Velocity(modal,{backgroundColor:color},{duration:0});
        Velocity(project.getElementsByClassName('flip-logo-back')[0],{backgroundColor:color},{duration:0});

        
        
        

        return project_object;
        
    }
    
    
    
    function openResearchModal(proj_name) {
    
        
        
        return function _openResearchModal() {
            
            document.body.style.overflowY = 'hidden';   
              
            research_projects.forEach(function(proj_el) {
                if(proj_name==proj_el.name)
                {
                    proj_el.button_open_modal.classList.add('active');
                    proj_el.active=true;
                }
            });
                                      
            //first of all put the modal into view
            research_modal_container.classList.add('front-view');
            
            
            var dock = document.getElementsByClassName('flying-dock')[0];
            
            //once everything is finished move the buttons to their position
            var dock_promise = Velocity(dock,{
                    top: 0,
                    left: 0
            },0);
            
            
            //make it appear
            dock_promise = dock_promise.then(function () {
                return Velocity(dock,'fadeIn',{duration:0,display:'flex'},0);
            });

            
            
            var modal_promise;
            
            research_projects.forEach(function _openResearchModalForEach(proj_el) {
                
                //get the current position of proj_el
                var rect = proj_el.button_open_modal.getBoundingClientRect();
                    
                var tmp_color = '';
                if(proj_name == proj_el.name)
                    tmp_color = proj_el.color;
                
                var p_flying = Velocity(proj_el.flying,{
                    backgroundColor:tmp_color,
                    top: rect.top + 'px',
                    height : rect.height.toString() + 'px',
                    left : rect.left.toString() + 'px',
                    width : rect.width.toString() + 'px'
                },0);
                
//                
//                //if is the active element color it
//                if(proj_name == proj_el.name)
//                    p_flying = p_flying.then(function () {
//                        return Velocity(proj_el.flying ,{backgroundColor: proj_el.color},{duration:0});
//                    });


                //make it appear
                p_flying = p_flying.then(function () {
                    return Velocity(proj_el.flying ,'fadeIn',{duration:0},0);
                });

                

                if(proj_name==proj_el.name)
                {   
                    var p_flying = Velocity(proj_el.modal_base,{
                        backgroundColor: proj_el.color,
                        position:'absolute',
                        top: (window.pageYOffset+rect.top).toString() + 'px',
                        height : rect.height.toString() + 'px',
                        left : rect.left.toString() + 'px',
                        width : rect.width.toString() + 'px'
                    },0);

                    //make it appear
                    p_flying = p_flying.then(function () {
                            return Velocity(proj_el.modal_base ,'fadeIn',0);
                    });
                

                    //prepare for the last expansion

                    //get maximum expansion
                    var radius = Math.round(2* Math.max(window.innerHeight, window.innerWidth));

                    //margin = -(new_size - (old_size+2*old_margin))/2
                    //better if is not float 
                    var margin = -Math.round((radius - rect.height) / 2);
                    var new_size = rect.height - 2 * margin;

                    

                    p_flying = p_flying.then(function () {
                        return Velocity(proj_el.modal_base,{
                            width : new_size + 'px',
                            height : new_size + 'px',
                            margin : margin + 'px'
                        },{
                            duration: timeModalRadius,
                            easing: "ease-in"   
                        });
                    });

                    modal_promise = p_flying;
                    
                    // change the color of the navigator links!
                    Velocity(navigator,{color:proj_el.color},{duration:timeModalOpacity});
                }
                


            });
         

            // for each element return a promise
            var logos_promises = Array(3);
            var tmp_cnt = 0;
            research_projects.forEach(function dockLogos(proj_el) {

                logos_promises[tmp_cnt++] = modal_promise.then(function () {
                    //go to the dummy's position
                    var rect = proj_el.dummy.getBoundingClientRect();

                    var tmp_promise = Velocity(proj_el.flying,{
                        top: rect.top + 'px',
                        left : rect.left + 'px',
                        height: rect.height + 'px',
                        width : rect.width + 'px',
                        easing: 'ease-in-out'
                    },{duration:timeModalFlying});
                    
                    tmp_promise.then(function () {
                        
                        var ip = Promise.resolve(0);
                        
                        if(proj_name == proj_el.name)
                            ip = Velocity(proj_el.dummy,{backgroundColor:proj_el.color},{duration:0});
    
                        ip = ip.then(function() {
                            return Velocity(proj_el.dummy,'fadeIn',{duration:0});
                        });
                                     
                        ip = ip.then(function() {
                            return Velocity(proj_el.flying,'fadeOut',{duration:0});
                        });
                        
                    });
                    
                    return tmp_promise;
                });

            });
            
            
            //finally make the modal appear
            Promise.all(logos_promises).then(function () {

                research_projects.forEach(function _openResearchModalForEach(proj_el) {

                    if(proj_name==proj_el.name)
                        Velocity(proj_el.modal,'fadeIn',{duration:timeModalOpacity});
                        
                });
            });
            
            

        }
        

        
    }
    
    
    
    function closeResearchModal(proj_name) {    
        
        return function _closeResearchModal() {
            
            var modal_promise;
            
            research_projects.forEach(function(proj_el) {
                
                if(proj_name == proj_el.name && proj_el.active)
                {

                    
                    //move the flying modal in position and make the modal disappear   
                    
                    
                    //get the position
                    var rect = proj_el.button_open_modal.getBoundingClientRect();

                    //get maximum expansion
                    var radius = Math.round(2* Math.max(window.innerHeight, window.innerWidth));

                    //margin = -(new_size - (old_size+2*old_margin))/2
                    //better if is not float 
                    var margin = -Math.round((radius - rect.height) / 2);
                    var expanded_size = rect.height - 2 * margin;


                    var tmp_promise = Velocity(proj_el.modal_base,{
                        backgroundColor:proj_el.color,
                        position:'absolute',
                        top: (window.pageYOffset+rect.top).toString() + 'px',
                        height : expanded_size + 'px',
                        left : rect.left.toString() + 'px',
                        width : expanded_size + 'px',
                        margin : margin + 'px'
                    },0);

                    //make it appear
                    tmp_promise = tmp_promise.then(function () {
                            return Velocity(proj_el.modal_base ,'fadeIn',0);
                    });

                    
                    
                    
                    
                    proj_el.active=false;
                    modal_promise = Velocity(proj_el.modal,'fadeOut',{duration:timeModalOpacity});
                }
                
            });
            
            
            if(modal_promise == undefined)
                return;
            
            modal_promise.then(function () {
                
                
                
                // for each element return a promise
                var logos_promises = Array(3);
                var tmp_cnt = 0;
                
                research_projects.forEach(function(proj_el) {
                
                    //first make the flying button appear beneath the dummy
                    var rect = proj_el.dummy.getBoundingClientRect();

                    var tmp_color = basicBackgroundColor;
                    if(proj_name == proj_el.name)
                        tmp_color = proj_el.color;
                    
                    var tmp_promise = Velocity(proj_el.flying,{
                        backgroundColor: tmp_color,
                        top: rect.top + 'px',
                        left : rect.left + 'px',
                        height: rect.height + 'px',
                        width : rect.width + 'px',
                    },{duration:0});
                    
                    tmp_promise = tmp_promise.then(function () {
                        return Velocity(proj_el.flying,'fadeIn',{duration:0}).then(function(){
                            return Velocity(proj_el.dummy,{backgroundColor:basicBackgroundColor,opacity:0},{duration:0});
                        });
                    });
                    
                    //then go back to the button position
                    tmp_promise = tmp_promise.then(function() {
                        
                        //get the current position of proj_el
                        rect = proj_el.button_open_modal.getBoundingClientRect();

                        return Velocity(proj_el.flying,{
                            top: rect.top + 'px',
                            height : rect.height.toString() + 'px',
                            left : rect.left.toString() + 'px',
                            width : rect.width.toString() + 'px',
                            easing: 'ease-in-out'
                        },{duration:timeModalFlying});
                    });


                    logos_promises[tmp_cnt++]=tmp_promise;
                    
                });
                
                //finally move the flying-modal under the button, reduce it and close everything
                var flying_modal_promise = Promise.all(logos_promises).then(function () {

                    var _flying_modal_promise;
                    
                    research_projects.forEach(function (proj_el) {

                        if(proj_name==proj_el.name)
                        {
                            //prepare for the shrinking
                            var rect = proj_el.button_open_modal.getBoundingClientRect();
                            
                            _flying_modal_promise = Velocity(proj_el.modal_base,{
                                height : rect.height.toString() + 'px',
                                width : rect.width.toString() + 'px',
                                margin: ''
                            },{
                                duration: timeModalRadius,
                                easing: "ease-out"   
                            });
                            
                            _flying_modal_promise = _flying_modal_promise.then(function(){                                
                                return Velocity(proj_el.modal_base,'fadeOut',{duration:0});
                            });
                            
                            // change the color of the navigator links!
                            Velocity(navigator,{color:basicBackgroundColor},{duration:timeModalOpacity});
                        }
                        
                    });
                    
                    return _flying_modal_promise;
                    
                });
                
                
                
                
                flying_modal_promise.then(function(){ 
                    
                    research_projects.forEach(function (proj_el) {
                
                        //conclude by setting everything back
                        if(proj_name==proj_el.name)
                        {
                            proj_el.active=false;
                        }
                        
                        
                        Velocity(proj_el.flying,'fadeOut',{
                            duration:0
                        }).then(function() {
                            Velocity(proj_el.flying,{backgroundColor:basicBackgroundColor},{duration:0});
                            proj_el.button_open_modal.classList.remove('active');
                        });
                        
                    });
                    
                    //set the modal back
                    research_modal_container.classList.remove('front-view');
                    
                    return Velocity(document.getElementsByClassName('flying-dock')[0],'fadeOut',{duration:0}).then(function() {
                        
                        
                        document.body.style.overflowY = 'auto';  
                    });
                });
                
            });

        }
        
    }
    
    
    
    function switchResearchModal(proj_name) {    
        
        
        return function _switchResearchModal() {
            
            research_projects.forEach(function(proj_el) {
            
                if(proj_name == proj_el.name && !proj_el.active)
                {
                    // change the color of the navigator links!
                    Velocity(navigator,{color:proj_el.color},{duration:timeModalOpacity});
                    
                    Velocity(proj_el.dummy,{backgroundColor:proj_el.color},timeModalOpacity);
                    
                    proj_el.button_open_modal.classList.add('active');
                    
                    Velocity(proj_el.modal,'fadeIn',timeModalOpacity);
                    proj_el.active=true;
                }
                
                if(proj_name != proj_el.name && proj_el.active)
                {   
                    Velocity(proj_el.dummy,{backgroundColor:basicBackgroundColor},timeModalOpacity);
                    
                    
                    proj_el.button_open_modal.classList.remove('active');
                    
                    Velocity(proj_el.modal,'fadeOut',timeModalOpacity);
                    proj_el.active=false;
                }
            });

        }
        
    }
    
    
    //add the callback to all of them
//    research_projects.forEach(function addClick(proj_el) {
//        proj_el.button_open_modal.addEventListener('click', openResearchModal(proj_el.name));
//        
//        proj_el.dummy.addEventListener('click', switchResearchModal(proj_el.name));
//        
//        proj_el.button_close_modal.addEventListener('click',closeResearchModal(proj_el.name));
//    });
    
    
    
    
    
    
    function getColorOfElement(el) {
        
        function rgb2Hex(r, g, b) {

            function component2Hex(c) {
                var hex = c.toString(16);
                return hex.length == 1 ? "0" + hex : hex;
            }

            return "#" + component2Hex(r) + component2Hex(g) + component2Hex(b);
        }

        
        var rgb = Velocity.hook(document.getElementsByTagName('a')[0],'color').split(' ');
     
        return rgb2Hex(rgb[0]-0,rgb[1]-0,rgb[2]-0);
    }
    
    
    
    //get all links in the navigator
    var links = navigator.getElementsByTagName('a');
    
    //need to call it lik this since it is a HTMLCollection
    Array.prototype.forEach.call(links, function addNavigatorCallback(link){
        link.addEventListener('click',function(){
           research_projects.forEach(function(proj_el){proj_el.closeModal();}); 
        });
    });
    
};



