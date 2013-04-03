/**
 * Created with IntelliJ IDEA.
 * User: xjc01266
 * Date: 24/09/12
 * Time: 4:44 PM
 * To change this template use File | Settings | File Templates.
 */

// Javascript for help icons/text
function toggleHelp(help_icon) {
    var help_text = $(help_icon.parentNode).find('.help_text');
    if (help_text.length <= 0) {
        help_text = $(help_icon.parentNode.parentNode).find('.help_text')
    }
    help_text.first().toggle(200);
    $(help_icon).toggleClass("current");

}

// Used as an onclick function for toggling a mapping schema
function toggleCollapse(fieldset, group) {
    var speed = 200;
    var collapsible_item = $(fieldset.parentNode).children('ul').first();

    if (collapsible_item.is(':hidden')) {
//        if (group != "None") {
//            $(".collapsible-" + group).find(".collapsible_items").slideUp(speed);
//            $(".collapsible-" + group).find(".collapse_icon").html('+');
//        }
        $(fieldset).children('.collapse_icon')[0].innerHTML = ('-');
        collapsible_item.slideDown(speed);
//        $(fieldset.parentNode).css("background-color", "transparent");
    } else {
        $(fieldset).children('.collapse_icon')[0].innerHTML = ('+');
        collapsible_item.slideUp(speed);
//        $(fieldset.parentNode).css("background-color", "#99FFFF");
    }
}

function collapseAll(group) {
    $('.collapsible-' + group).find('.collapsible_items').slideUp(200);
}

function expandAll(group) {
    $('.collapsible-' + group).find('.collapsible_items').slideDown(200);
}


function escapeQuotes(text) {
    var i = 0;
    var text_array = text.split("'");
    text = "";
    for (i; i < text_array.length - 1; i++) {
        text = text.concat(text_array[i], "\\'");
    }
    text = text.concat(text_array[text_array.length - 1]);

    var text_array = text.split('"');
    text = "";
    for (i; i < text_array.length - 1; i++) {
        text = text.concat(text_array[i], '\\"');
    }
    text = text.concat(text_array[text_array.length - 1]);

    return text;
}

function submitClearsDefaultValues(oid, default_text) {
    var form = document.getElementById('deform');
    default_text = escapeQuotes(default_text);

    var submit_text = "if (document.getElementById('" + oid + "') != null && document.getElementById('" + oid + "').value == '" + default_text + "') {document.getElementById('" + oid + "').value = '';}";

    if (form.getAttribute('onsubmit') != null) {
        submit_text += form.getAttribute('onsubmit');
    }
    form.setAttribute('onsubmit', submit_text);
}

function hideDescriptions(hide) {
    document.hide_descriptions = hide;

    if (hide) {
        $(".description").addClass("hidden");
    } else {
        $(".description").removeClass("hidden");
    }
}


/*function fixHTMLTags(descText) {
 while (descText.match("\&lt;")) {
 descText = descText.replace("\&lt;", "<");
 }

 while (descText.match("\&gt;")) {
 descText = descText.replace("\&gt;", ">");
 }

 return descText;
 }

 $(document).ready(function () {

 });
 */


//--------------------------Map_sequence Template------------------------------------

function findMapLayerFromFeature(feature, map) {
    var i = 0, j = 0, k = 0;
    if (typeof map === "undefined") {
        for (i; i < document.location_maps.length; i++) {
            for (j; j < document.location_maps[i].layers.length; j++) {
                if ((OpenLayers.Layer.Vector.prototype.isPrototypeOf(document.location_maps[i].layers[j]))) {
                    for (k; k < document.location_maps[i].layers[j].features.length; k++) {
                        if (document.location_maps[i].layers[j].features[k] == feature) {
                            return document.location_maps[i].layers[j];
                        }
                    }
                }
            }
        }
    } else {
        for (j; j < document.location_maps[i].layers.length; j++) {
            if ((OpenLayers.Layer.Vector.prototype.isPrototypeOf(document.location_maps[i].layers[j]))) {
                for (k; k < document.location_maps[i].layers[j].features.length; k++) {
                    if (document.location_maps[i].layers[j].features[k] == feature) {
                        return document.location_maps[i].layers[j];
                    }
                }
            }
        }
    }

    return null;
}

function findMapFromLayer(layer) {
    var i = 0, j = 0, k = 0;
    for (i; i < document.location_maps.length; i++) {
        for (j; j < document.location_maps[i].layers.length; j++) {
            if (document.location_maps[i].layers[j] == layer) {
                return document.location_maps[i];
            }
        }
    }
    return null;
}

function appendSequenceItem(add_link) {
    deform.appendSequenceItem(add_link);
    var fields = $(add_link.parentNode).children('ul').first().find("input[type=text].map_location");
    fields[fields.length - 1].setAttribute("onblur", "locationTextModified(this);");
    fields[fields.length - 1].map_div = $(add_link.parentNode).children(".location_map")[0];

    var deleteLink = $(fields[fields.length - 1]).parents("li").children('.deformClosebutton')[0];
    deleteLink.setAttribute("onclick", deleteLink.getAttribute("onclick") + " deleteFeature($(this.parentNode).find('input[type=text]')[1].feature);");
}

function addMapFeatures(oid) {
    var fields = $("#" + oid).children('ul').first().find("input[type=text].map_location");
    var map_div = $("#" + oid).children(".location_map")[0];

    var i = 0;
    for (i; i < fields.length; i++) {
        var deleteLink = $(fields[i]).parents("li").children('.deformClosebutton')[0];
        deleteLink.setAttribute("onclick", deleteLink.getAttribute("onclick") + " deleteFeature($(this.parentNode).find('input[type=text]')[1].feature);");

        fields[i].setAttribute("onblur", "locationTextModified(this);");
        fields[i].map_div = map_div;
        locationTextModified(fields[i]);
    }
}

function locationTextModified(input) {
    var geometry_type = input.value.substr(0, input.value.indexOf("("));
    var displayProj = new OpenLayers.Projection("EPSG:4326");
    var proj = new OpenLayers.Projection("EPSG:900913");

    var newGeometry;

    var point_match = /point\([+-]?\d*\.?\d* [+-]?\d*\.?\d*\)/i;
    var poly_match = /polygon\(\(([+-]?\d*\.?\d*\s[+-]?\d*\.?\d*,?\s?)*\)\)/i;
    var line_match = /linestring\(([+-]?\d*\.?\d*\s[+-]?\d*\.?\d*,?\s?)*\)/i;

    var points, text_points, i = 0;
    if (input.value.match(point_match)) {
        points = input.value.trim().substring(geometry_type.length + 1, input.value.trim().length - 1).split(" ");
        newGeometry = new OpenLayers.Geometry.Point(new Number(points[0]), new Number(points[1]));
    } else if (input.value.match(poly_match)) {
        text_points = input.value.trim().substring(geometry_type.length + 2, input.value.trim().length - 2).split(",");
        points = [];
        for (i; i < text_points.length; i++) {
            points.push(new OpenLayers.Geometry.Point(new Number(text_points[i].split(" ")[0]), new Number(text_points[i].split(" ")[1])));
        }
        newGeometry = new OpenLayers.Geometry.Polygon(new OpenLayers.Geometry.LinearRing(points));
    } else if (input.value.match(line_match)) {
        text_points = input.value.trim().substring(geometry_type.length + 1, input.value.trim().length - 1).split(",");
        points = [];
        for (i; i < text_points.length; i++) {
            points.push(new OpenLayers.Geometry.Point(new Number(text_points[i].split(" ")[0]), new Number(text_points[i].split(" ")[1])));
        }
        newGeometry = new OpenLayers.Geometry.LineString(points);
    } else {
        input.style.background = "#ffaaaa";
        return;
    }

    newGeometry.transform(displayProj, proj);
    input.style.background = "white";

    var layer;
    var j = 0, k = 0;
    for (i = 0; i < document.location_maps.length; i++) {
        if (document.location_maps[i].div == input.map_div) {
            for (j; j < document.location_maps[i].layers.length; j++) {
                if ((OpenLayers.Layer.Vector.prototype.isPrototypeOf(document.location_maps[i].layers[j]))) {
                    layer = document.location_maps[i].layers[j];
                    break;
                }
            }
        }
    }

    var new_feature = new OpenLayers.Feature.Vector(newGeometry);

    if (input.hasOwnProperty('feature')) {
        layer.destroyFeatures([input.feature]);
        input.feature = new_feature;
        layer.addFeatures([new_feature]);
    } else {
        input.feature = new_feature;
        layer.addFeatures([new_feature]);
    }
}

function modifyFeature(object) {
    var feature = object.feature;
    var map = object.object.map;
    var layer = findMapLayerFromFeature(feature, map);
    var oid_node = $(map.div.parentNode);
    var fields = oid_node.children('ul').first().find("input[type=text]");

    var displayProj = new OpenLayers.Projection("EPSG:4326");
    var proj = new OpenLayers.Projection("EPSG:900913");
    var geometry = feature.geometry.clone();
    geometry.transform(map.getProjectionObject(), displayProj);

    var i = 0;
    for (i; i < fields.length; i++) {
        if (fields[i].feature == feature) {
            fields[i].value = geometry;
        }
    }
}

function deleteFeature(feature) {
    var layer = findMapLayerFromFeature(feature);

    var map = findMapFromLayer(layer);
    var displayProj = new OpenLayers.Projection("EPSG:4326");

    var oid_node = $(map.div.parentNode);
    var geometry = feature.geometry.clone();
    geometry.transform(map.getProjectionObject(), displayProj);

    var fields = oid_node.children('ul').first().find("input[type=text]");
    var i = 0;
    for (i; i < fields.length; i++) {
        if (fields[i].value == geometry.toString()) {
            deform.removeSequenceItem($(fields[i].parentNode.parentNode.parentNode.parentNode.parentNode).find(".deformClosebutton"));
        }
    }

    feature.destroy();
}

function featureInserted(object) {
    var feature = object.feature;
    var displayProj = new OpenLayers.Projection("EPSG:4326");
    var proj = new OpenLayers.Projection("EPSG:900913");
    var map = object.object.map;
    var layer = feature.layer; //findMapLayerFromFeature(feature, map);

    var oid_node = $(map.div.parentNode);
    var fields = oid_node.children('ul').first().find("input[type=text].map_location");

    // Check if this feature already has an associated input
    var i = 0;
    for (i; i < fields.length; i++) {
//        var tmp = feature.geometry.clone();
//        tmp.transform(map.getProjectionObject(), displayProj);
        if (fields[i].feature == feature) {
            return;
        }
    }


//            var i = 0, j = 0;
//            for (i; i < layer.features.length; i++) {
//                /*alert((OpenLayers.Geometry.Polygon.prototype.isPrototypeOf(layer.features[i].geometry)));*/
//                alert(layer.features[i].geometry);
//                alert(displayProj + " : " + proj + " : " + map.getProjection() + " : " + map.getProjectionObject());
//                for (j; j < layer.features[i].geometry.getVertices().length; j++) {
//                    vertices += layer.features[i].geometry.getVertices()[j].transform(map.getProjectionObject(),displayProj) + ", ";
//                }
//            }
    /*   alert(vertices);*/


    // Only add a new feature if the last item in the list isn't blank
    var last_field = fields[fields.length - 1];
    var siblings = $(last_field.parentNode.parentNode).siblings().find("input[type=text]");
    if (last_field.value != '' || last_field.feature !== undefined || siblings[0].value != '' || siblings[1].value != '') {
        /* Add the feature */
        appendSequenceItem(oid_node.children(".deformSeqAdd")[0]);
    }

    fields = oid_node.children('ul').first().find("input[type=text].map_location");

    var geometry = feature.geometry.clone();
    geometry.transform(map.getProjectionObject(), displayProj);


    fields[fields.length - 1].value = geometry;
    fields[fields.length - 1].feature = feature;
    fields[fields.length - 1].className = fields[fields.length - 1].className.replace( /(?:^|\s)placeholder_text(?!\S)/g , '' );
}

//--------------------conditional_heckbox_mapping.pt----------------
function displayConditionalCheckboxItems(checkboxElement) {
    var contentDiv = $(checkboxElement.parentNode).children(".checkbox_mapping_content")[0];
    if (checkboxElement.checked) {

//        if (contentDiv.hasOwnProperty('previousContent')) {
//            contentDiv.innerHTML = contentDiv.previousContent;
//            processJavascript(contentDiv);
//            deform.processCallbacks();
//        } else {
        var prototypes = $(checkboxElement.parentNode).children(".checkbox_mapping_prototypes").children(".checkbox_mapping_prototype");

        var content = "";
        var i = 0;
        for (i; i < prototypes.length; i++) {
            content += prototypes[i].value;
        }
        contentDiv.innerHTML = content;
        processJavascript(contentDiv);
        deform.processCallbacks();
//        }

    } else {
        contentDiv.previousContent = contentDiv.innerHTML;
        contentDiv.innerHTML = "";
    }
}

//------------------select_mapping.pt---------------------------
function setSelectedItem(select_element) {
    var protos = $("#select_mapping_prototypes-" + select_element.id).children(".select_mapping_prototype");

    var i = 0;
    var selectedProto;
    for (i; i < protos.length; i++) {
        if (protos[i].id.indexOf(select_element.value) >= 0) {
            selectedProto = protos[i];
            break;
        }
    }
    if (selectedProto == undefined) {
        return;
    }

//     var newHTML = (typeof selectedProto == 'undefined' ? "" : selectedProto.value);
//    alert($(selectedProto).attr('prototype'));
    $(selectedProto).attr('prototype', encodeURIComponent($(selectedProto).attr('prototype')));
    var $proto_node = $(selectedProto);
    var $before_node = $("#select_mapping_content-" + select_element.id).find('.deformInsertBefore');
    var min_len = parseInt('0');
    var max_len = parseInt('9999');
    var now_len = parseInt('0');
    deform.addSequenceItem($proto_node, $before_node);

//     document.getElementById("select_mapping_content-" + select_element.id).innerHTML = newHTML;

//    var scripts = $("#select_mapping_content-" + select_element.id).find("script");
//
//    for (i = 0; i < scripts.length; i++) {
//        if (scripts[i].innerHTML.trim().length > 0) {
//            eval(scripts[i].innerHTML);
//        } else if (scripts[i].src.length > 0) {
//            $.getScript(scripts[i].src);
//        }
//    }
//    processJavascript($("#select_mapping_content-" + select_element.id)[0]);
//    deform.processCallbacks();
}

function processJavascript(parentElement) {
    var scripts = $(parentElement).find("script");

    for (i = 0; i < scripts.length; i++) {
        if (scripts[i].innerHTML.trim().length > 0) {
            eval(scripts[i].innerHTML);
        } else if (scripts[i].src.length > 0) {
            $.getScript(scripts[i].src);
        }
    }
}

//--------------multi_select_sequence.pt----------------------------------------------
function buttonPressed(node) {
    var oid_node = $(node).parent();
    var id = oid_node.attr('id');

    var first_select = oid_node.children(".first_field")[0];
    var second_select = oid_node.children(".second_field")[0];
    var third_select = oid_node.children(".third_field")[0];

    var fields = oid_node.children('ul').first().find("input[readonly='readonly']");

    var text = third_select.options[third_select.selectedIndex].value;

    if (text == "---Select One---") {
        var text = second_select.options[second_select.selectedIndex].value;
    }

    fields[fields.length - 1].value = text;
    fields[fields.length - 1].style.display = "inline";
    var removeButton = $(fields[fields.length - 1]).parents('[id^="sequence"]').find(".deformClosebutton")[0];
    removeButton.setAttribute("onclick","deform.removeSequenceItem(this);" + "showAdd('" + id + "', false);");
//    removeButton.onclick = removeButton.onclick + "; showAdd(" + oid_node[0].id + ", false); ";

    /* Delete duplicates */
    var i = 0;
    for (i; i < fields.length - 1; i++) {
        if (fields[i].value == text) {
            deform.removeSequenceItem($(fields[i]).parents('[id^="sequence"]').find(".deformClosebutton")[0]);
            alert("Not Added: The selected FOR code is a duplicate");
        }
    }
    /* Reset the FOR field select boxes */
    first_select.selectedIndex = 0;
    second_select.innerHTML = "";
    second_select.style.display = "none";
    $(second_select).next().hide();
    third_select.innerHTML = "";
    third_select.style.display = "none";
    $(third_select).next().hide();

    showAdd(oid_node[0].id, false);
}

function fix_multi_select_close(oid) {
    var oid_node = $('#' + oid);
    var close_buttons = oid_node.children('ul').first().find("span.deformClosebutton");
    for (var i=0; i<close_buttons.length; i++) {
        close_buttons[i].setAttribute("onclick","deform.removeSequenceItem(this);" + "showAdd('" + oid + "', false);");
    }
}

function showAdd(oid, show) {
    var oid_node = $('#' + oid);
//    alert(oid_node);

    var $before_node = oid_node.children('ul').first().children('.deformInsertBefore').first();
    var max_len = parseInt($before_node.attr('max_len')||'9999', 10);
    var now_len = parseInt($before_node.attr('now_len')||'0', 10);
    if (now_len >= max_len) {
        oid_node.children("button").hide();
        oid_node.children(".max_error").show();
        return;
    }
    oid_node.children(".max_error").hide();

    if (show) {
        oid_node.children("button")[0].style.display = "inline";
        var original_color = oid_node.children("button").first().css('backgroundColor');
        oid_node.children("button").animate({ backgroundColor: "#F7931E"}, 100);
        oid_node.children("button").animate({ backgroundColor: original_color}, 100);
        oid_node.children("button").animate({ backgroundColor: "#F7931E"}, 100);
        oid_node.children("button").animate({ backgroundColor: original_color}, 100);

//        alert('show');
    } else {
//        alert('hide');
        oid_node.children("button")[0].style.display = "none";
    }
}

function updateSecondFields(oid) {
    var oid_node = $('#' + oid);

    var first_select = oid_node.children(".first_field")[0];
    var second_select = oid_node.children(".second_field")[0];
    var third_select = oid_node.children(".third_field")[0];

    if (first_select.selectedIndex != 0) {
        var options_class = "second_level_data-" + first_select.options[first_select.selectedIndex].value;
        var second_level_options = document.getElementsByClassName(options_class)[0];
        second_select.innerHTML = second_level_options.innerHTML;
        second_select.style.display = "inline";
        $(second_select).next().show();
    } else {
        second_select.innerHTML = "";
        first_select.selectedIndex = 0;
        second_select.style.display = "none";
        $(second_select).next().hide();
        showAdd(oid, false);
    }
    third_select.innerHTML = "";
    third_select.style.display = "none";
    $(third_select).next().hide();
    /* Make sure that the user can't have an invalid 3rd field selected when the first select is changed */
}

function updateThirdFields(oid) {
    var oid_node = $('#' + oid);

    var first_select = oid_node.children(".first_field")[0];
    var second_select = oid_node.children(".second_field")[0];
    var third_select = oid_node.children(".third_field")[0];

    if (second_select.selectedIndex != 0) {
        var options_class = "third_level_data-" + second_select.options[second_select.selectedIndex].value;
        var third_level_options = document.getElementsByClassName(options_class)[0];
        third_select.innerHTML = third_level_options.innerHTML;
        third_select.style.display = "inline";
        $(third_select).next().show();
    } else {
        third_select.innerHTML = "";
        third_select.style.display = "none";
        $(third_select).next().hide();
        showAdd(oid, false)
    }
}
