function post_json(path, data) {
    return post(path, data).then((response) => {
        return response.json()
    })
}

function post(path, data) {
    return window.fetch(path, {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(data)
    });
}


var add_gen = document.getElementById('add_gen');
var predict = document.getElementById('predict');
var gen = document.getElementById('gen');
var more_genes = document.getElementById('more_genes');
var image_result = document.getElementById('image_result');
var count = 2;

add_gen.addEventListener("click", function(evt){
    var html = gen.innerHTML;
    console.log(html)
    var newdiv = document.createElement('div');
    newdiv.setAttribute("class", "gen");
    newdiv.innerHTML = html;
    newdiv.getElementsByTagName("label")[0].innerHTML = "Gene "+count;
    more_genes.appendChild(newdiv);
    count+=1;
});

predict.addEventListener("click", function(evt){
    var genes_dom = document.getElementsByClassName("gen");
    var genes_list = {}

    for (var i = 0; i < genes_dom.length; i++) {

       var sel = genes_dom.item(i).getElementsByClassName("select")[0]; 
       
       var gene_name = sel.options[sel.selectedIndex].text;

       var gene_val =parseInt(genes_dom.item(i).getElementsByClassName("range")[0].value);

       genes_list[gene_name] = gene_val
    }

	post_json("/generate_image",{"genes":genes_list}).then(data => {
        image_result.src = data["encoded"]
	}).catch(err => {
	    console.log({ err })
	})
    
	evt.preventDefault();
});