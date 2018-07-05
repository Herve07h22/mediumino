
selected = '2018';

	
$('#full').click(function()
	{
		$('#view-mode').children().removeClass('active');
		$('#full').addClass('active');
		$('.story-list').removeClass('compact');
	});

$('#compact').click(function()
	{
	$('#view-mode').children().removeClass('active');
	$('#compact').addClass('active');$('.story-list').addClass('compact');
	});
	
$('#all').click(function()
	{
	$('#filter').children().removeClass('active');
	$('#all').addClass('active');
    $('.story-list').hide();
	$('.load-more').hide();
	selected='all';
	if($(`#${selected}-story-list>div`).length<40){ load(40); }
    $('#all-story-list').show();
	$('#all-load').show();
	});

$('#2018').click(function() {
	
	$('#filter').children().removeClass('active');
	$('#2018').addClass('active');
    $('.story-list').hide();
	$('.load-more').hide();
	selected='2018';
	$('#2018-story-list').show();
	$('#2018-load').show();
	}
);

$('#2017').click(function() {
	
	$('#filter').children().removeClass('active');
	$('#2017').addClass('active');
    $('.story-list').hide();
	$('.load-more').hide();
	selected='2017';
	if($(`#${selected}-story-list>div`).length<40){ load(40); }
	$('#2017-story-list').show();
	$('#2017-load').show();
	}
);

$('#2016').click(function(){
	$('#filter').children().removeClass('active');
	$('#2016').addClass('active');
	$('.story-list').hide();
	$('.load-more').hide();
	selected='2016';
	if($(`#${selected}-story-list>div`).length<40){ load(40); }
	$('#2016-story-list').show();
	$('#2016-load').show();
	}
);

$('#2015').click(function(){
	$('#filter').children().removeClass('active');
	$('#2015').addClass('active');
	$('.story-list').hide();
	$('.load-more').hide();
	selected='2015';
	if($(`#${selected}-story-list>div`).length<40){ load(40); }
	$('#2015-story-list').show();
	$('#2015-load').show();
	}
);

$('#2014').click(function(){
	$('#filter').children().removeClass('active');
	$('#2014').addClass('active');
	$('.story-list').hide();
	$('.load-more').hide();
	selected='2014';
	if($(`#${selected}-story-list>div`).length<40){ load(40); }
	$('#2014-story-list').show();
	$('#2014-load').show();
	}
);
	
$('#2013').click(function(){
	$('#filter').children().removeClass('active');
	$('#2013').addClass('active');
	$('.story-list').hide();
	$('.load-more').hide();
	selected='2013';
	if($(`#${selected}-story-list>div`).length<40){ load(40); }
	$('#2013-story-list').show();
	$('#2013-load').show();
	}
);

$('.load-more').click(function(){load(40);});

function load(num){
	$.getJSON('medium.json',function(stories){
        document.getElementById("waiting").innerHTML += '<p><center> <img src="wait.gif"> </center></p>'
        var storyLength=$(`#${selected}-story-list>div`).length;
		var $storyList=$(`#${selected}-story-list`);
		var i=0;$.each(stories,function(key,val){
			var title=val[0];
			var year=val[1]['year'];
			var author=val[1]['author'];
			var author_url=val[1]['author_url'];
			var pub=val[1]['pub'];
			var pub_url=val[1]['pub_url'];
			var image=val[1]['image'];
			var story_url=val[1]['story_url'];
			var recommends=parseInt(val[1]['recommends']).toString();
			if(recommends.length>3){
				recommends=recommends.slice(0,-3)+','+ recommends.slice(-3);
			}
			if(selected=='all'||selected==year){
				if(i>=storyLength){
					var $story=$('<div>',{'class':'story'});
					var $index=$('<div>',{'class':'index','text':(i+ 1).toString()});
					$story.append($index);
					var $imageLink=$('<a>',{'class':'image','href':story_url});
					var $img=$('<img>',{'src':image});
                    $imageLink.append($img);
					$story.append($imageLink);
					var $infoLink=$('<div>',{'class':'info'});
					var $title=$('<a>',{'class':'title','text':title,'href':story_url});
					var $author=$('<a>',{'class':'author','text':author,'href':author_url});
					$infoLink.append($title);
					$infoLink.append($author);
					if(pub){
						var $separator=$('<span>',{'class':'separator','text':' in '});
						var $pub=$('<a>',{'class':'pub','text':pub,'href':pub_url});
						$infoLink.append($separator);$infoLink.append($pub);
					}
					$story.append($infoLink);
					$recommends=$('<div>',{'class':'recommends','text':recommends+' '});
					$clap=$('<img>',{'src':'clap.png'});
					$recommends.append($clap);
					$story.append($recommends);
					$storyList.append($story);
				}
				i++;
				if(i==storyLength+ num){
					return false;
				}
			}
		}
		);
		if(i==500){
			$(`#${selected}-load`).hide();
		}
        console.log('Apres chargement');
        document.getElementById("waiting").innerHTML = "";
	});
}