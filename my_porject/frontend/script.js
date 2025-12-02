const add_type_name=document.getElementById("add_type_name");
const add_type_describe=document.getElementById("add_type_describe");
const result_box=document.getElementById("result_box");
const types_table=document.getElementById("types_table");
const add_item_typename=document.getElementById("add_item_typename");
const add_item_count=document.getElementById("add_item_count");
const delete_item_typename=document.getElementById("delete_item_typename");
const delete_item_count=document.getElementById("delete_item_count");
const apiurl="/api/";

let result_pre=document.createElement("pre");
result_box.appendChild(result_pre);
function update_result(d,data){
    if(result_pre!==null) result_box.removeChild(result_pre);
    result_pre=document.createElement("pre");
    result_pre.appendChild(document.createTextNode(d.is_200?
        data.message:
        "Error:status="+d.status.toString()+",detail:"+JSON.stringify(data.detail,null,4)
    ));
    result_box.appendChild(result_pre);
}

function error_result(error){
    if(result_pre!==null) result_box.removeChild(result_pre);
    result_pre=document.createElement("pre");
    result_pre.appendChild(document.createTextNode(error));
    result_box.appendChild(result_pre);
}

function add_type(){
    let d={
        is_200:true,
        status:0
    }
    fetch(apiurl+"add_type/",{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({
            name:add_type_name.value,
            describe:add_type_describe.value,
            pw:"123456"
        })
    })
    .then(response =>{
        if(!response.ok){
            d.is_200=false;
            d.status=response.status;
        }
        return response.json();
    })
    .then(data=>{
        console.log(data);
        update_result(d,data);
    })
    .catch(error=>{
        console.error("Error:", error);
        error_result(error);
    });
}

let columns_names=["id","name","describe","count"];
let prev_arr=[];
function get_types(){
    let d={
        is_200:true,
        status:0
    }
    fetch(apiurl+"get_types/",{method:'GET'})
    .then(response =>{
        if(!response.ok){
            d.is_200=false;
            d.status=response.status;
        }
        return response.json();
    })
    .then(data=>{
        console.log(data);
        update_result(d,data);
        let types=data.data;
        for(let i=0;i<prev_arr.length;i++) types_table.removeChild(prev_arr[i]);
        prev_arr=[];
        for(let i=0;i<types.length;i++){
            const new_tr=document.createElement("tr");
            for(let j=0;j<columns_names.length;j++){
                const new_td=document.createElement("td");
                new_td.appendChild(document.createTextNode(JSON.stringify(types[i][columns_names[j]])));
                new_tr.appendChild(new_td);
            }
            types_table.appendChild(new_tr);
            prev_arr.push(new_tr);
        }
    })
    .catch(error=>{
        console.error("Error:", error);
        error_result(error);
    });
}

function clear_types(){
    for(let i=0;i<prev_arr.length;i++) types_table.removeChild(prev_arr[i]);
    prev_arr=[];
}

function add_item(){
    let d={
        is_200:true,
        status:0
    }
    fetch(apiurl+"add_item/",{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({
            typename:add_item_typename.value,
            count:add_item_count.value,
            pw:"123456"
        })
    })
    .then(response =>{
        if(!response.ok){
            d.is_200=false;
            d.status=response.status;
        }
        return response.json();
    })
    .then(data=>{
        console.log(data);
        update_result(d,data);
    })
    .catch(error=>{
        console.error("Error:", error);
        error_result(error);
    });
}

function delete_item(){
    let d={
        is_200:true,
        status:0
    }
    fetch(apiurl+"delete_item/",{
        method:'DELETE',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({
            typename:delete_item_typename.value,
            count:delete_item_count.value,
            pw:"123456"
        })
    })
    .then(response =>{
        if(!response.ok){
            d.is_200=false;
            d.status=response.status;
        }
        return response.json();
    })
    .then(data=>{
        console.log(data);
        update_result(d,data);
    })
    .catch(error=>{
        console.error("Error:", error);
        error_result(error);
    });
}

const button1=document.getElementById("button1");
button1.addEventListener("click",add_type);

const button2_1=document.getElementById("button2_1");
button2_1.addEventListener("click",get_types);

const button2_2=document.getElementById("button2_2");
button2_2.addEventListener("click",clear_types);

const button3=document.getElementById("button3");
button3.addEventListener("click",add_item);

const button4=document.getElementById("button4");
button4.addEventListener("click",delete_item);


