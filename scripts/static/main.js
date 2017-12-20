var baseUrl = "";
//var baseUrl = "";
var app_key = "tSAOAAgliQChZfKp7xSQ6uJmOtePqiL1";
var ixSearchUrl = "https://api.indix.com/v2.1/search?app_key="+app_key;
var regex = new RegExp(".*products/(.*)\\\?.*")
function populateProducts (products) {
  $("#products").empty();
  products.forEach(function (product) {
    regex.lastIndex = 0
    $("#products").append('<div class="col-sm-12 p-card">'+
    '<div class="row">'+
      '<div class="thumbnail col-sm-4 text-center">'+
        '<img style="max-height:100px;padding-left: 10px;" src="'+ (product.image ? product.image.url : product.modelImageUrl) +'"/>'+
      '</div>'+
      '<div class="caption col-sm-8">'+
        '<div style="font-family: Arial; font-size: 16px;text-overflow: ellipsis;overflow: hidden; white-space: nowrap;">'+ product.title +'</div>'+
        '<span style="font-family: Arial; font-size: 11px;">'+product.categoryNamePath+'</span>'+
        // '<span style="font-family: Arial; font-size: 11px;">storeId: '+product.priceRange[0].storeId+'</span>'+
        // '<span> RatingCount '+ product.aggregatedRatings.ratingCount + '</span><span> RatingValue '+ product.aggregatedRatings.ratingValue +'</span>'+
        '<div class="clearfix">'+
          '<div class="tags float-left" style="font-family: Arial; font-size: 11px;">'+product.brandName+'</div>'+
          '<div class="tags float-left" style="font-family: Arial; font-size: 11px;">searchScore: '+product.searchScore+'</div>'+
          // '<div class="tags float-left" style="font-family: Arial; font-size: 11px;">$'+ product.priceRange[0].salePrice+' - '+ product.priceRange[1].salePrice +'</div>'+
          '<div class="tags float-left" style="font-family: Arial; font-size: 11px;">mpid: '+(product.mpid || regex.exec(decodeURIComponent(product.detailsUrl))[1])+'</div>'+
          '<div class="tags float-left" style="font-family: Arial; font-size: 11px;">sku: '+ (product.sku ? product.sku : Object.keys(product.stores || {})[0] ? (((product.stores[Object.keys(product.stores || {})[0]] || {}).offers || [])[0] || {}).sku : undefined)+'</div>'+
        '</div>'+
      '</div>'+
    '</div>'+
  '</div>');
  });
}

function populateProductsByType (type, products, responseTime) {
  var dom;
  switch (type) {
    case 'api':
      dom = $('#apiProducts'); 
      $("#api_time").text(`( ${responseTime.toFixed(2)} s )`);
      break;
    case 'gatsby':
      dom = $('#gatsbyProducts'); 
      $("#gatsby_time").text(`( ${responseTime.toFixed(2)} s )`)
      break;
    case 'thunderbird':
      dom = $('#thunderbird'); 
      $("#thunderbird_time").text(`( ${responseTime.toFixed(2)} s )`)
      break;
  }
  dom.empty();
  products.forEach(function (product) {
    regex.lastIndex = 0
    const mpid = regex.exec(decodeURIComponent(product.detailsUrl || ""))
    dom.append('<div class="col-sm-12 p-card">'+
    '<div class="row">'+
      '<div class="thumbnail col-sm-4 text-center">'+
        '<img style="max-height:100px;padding-left: 10px;" src="'+ (product.image ? product.image.url : product.modelImageUrl) +'"/>'+
      '</div>'+
      '<div class="caption col-sm-8">'+
        '<p><div style="font-family: Arial; font-size: 16px;text-overflow: ellipsis;overflow: hidden; white-space: nowrap;">'+ product.title +'</div>'+
        '<span style="font-family: Arial; font-size: 11px;">'+product.categoryNamePath+'<br>'+
        // '<span style="font-family: Arial; font-size: 11px;">storeId: '+product.priceRange[0].storeId+'</span>'+
        // '<span> RatingCount '+ product.aggregatedRatings.ratingCount + '</span><span> RatingValue '+ product.aggregatedRatings.ratingValue +'</span></p>'+
        '<div class="clearfix">'+
          '<div class="tags float-left" style="font-family: Arial; font-size: 11px;">'+product.brandName+'</div>'+
          '<div class="tags float-left" style="font-family: Arial; font-size: 11px;">searchScore: '+product.searchScore+'</div>'+
          // '<div class="tags float-left" style="font-family: Arial; font-size: 11px;">$'+ product.priceRange[0].salePrice+' - '+ product.priceRange[1].salePrice +'</div>'+
          '<div class="tags float-left" style="font-family: Arial; font-size: 11px;">mpid: '+(product.mpidStr || product.mpid || mpid[1])+'</div>'+
          '<div class="tags float-left" style="font-family: Arial; font-size: 11px;">sku: '+ (product.sku ? product.sku : Object.keys(product.stores || {})[0] ? (((product.stores[Object.keys(product.stores || {})[0]] || {}).offers || [])[0] || {}).sku : undefined) +'</div>'+
        '</div>'+
      '</div>'+
    '</div>'+
  '</div>');
  });
}

function populateStatus (query, count, tags) {
  $("#sidebar").empty();
  $("#sidebar").append(
    '<p> Matched '+ count +'<br><br>'+
    'Refined Query:'+ query.replace(/\&/g, '<br>&nbsp;') +
    '</p><br><br>'
  );

  // Dumping the tags from /api/tags
  $('#sidebar').append('<pre>'+
    JSON.stringify(tags) +
    '</pre>'
  );
}


function getProducts(tags, query) {

  var queryStr = '&countryCode=IN&q=' + query;

  $.getJSON(ixSearchUrl + queryStr, null, function (resp) {
    console.log("Actual Search ", resp.result);
    populateProducts(resp.result.products, resp.result.count);
  });

}

function getBrands() {

}

function getStores () {

}

function getCategories() {

}

function getRefinedProducts(tags, query) {

  var queryStr = '&countryCode=IN&pageSize=20';

  if (query)
    queryStr += ("&q=" + query);

  tags.brands.forEach(function (brand) {
    queryStr += brand.matches.map(function (brandId) {
      return "&brandId=" + brandId;
    }).join('');
  });

  tags.stores.forEach(function (store) {
    queryStr += store.matches.map(function (storeId) {
      return "&storeId=" + storeId;
    }).join('');
  });

  tags.categories.forEach(function (categ) {
    queryStr += categ.matches.map(function (categId) {
      return "&categoryId=" + categId;
    }).join('');
  });

  $.getJSON(ixSearchUrl + queryStr, null, function (resp) {
    console.log("products: ", resp);
    populateProducts(resp.result.products, resp.result.count);
    populateStatus(queryStr, resp.result.count, tags);
  });
}
function getTBParams() {
  const hashes = location.hash.replace("#", "").split("&")
  return hashes.reduce((acc, hash) => {
    const [name, value] = hash.split("=")
    return Object.assign({}, acc, { [name]: (value == "true") ? true : false })
  }, {})
}
function query () {
  var searchText = $('.btn-search').text();
  $('.btn-search').text('Searching..');

  var q = $("#query").val();
  var sortBy = $('select[name="sort_by"]').val();
  var storeIds = $('#store_id').val();

  if (!q) {
      alert("Please enter valid search term!!!");
      $('.btn-search').text('Search');
      return;
  }
  var params = {
    q: q,
    sort_by: sortBy,
    store_ids: storeIds.join(','),
    tb_params: getTBParams()
  };
  console.log(params);

  $.getJSON(baseUrl+"/api/products", params,
    function (resp) {
      $('.btn-search').text(searchText);
      populateProductsByType('api', resp.api.products, resp.api.responseTime)
      populateProductsByType('gatsby', resp.gatsby.products, resp.gatsby.responseTime)
      populateProductsByType('thunderbird', resp.tb_api.products, resp.tb_api.responseTime)
   })
}

$("#query").on('keyup', function (e) {
    if (e.keyCode == 13) {
        query();
    }
});
