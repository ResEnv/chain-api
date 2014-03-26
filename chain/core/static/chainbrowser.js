/*
{% macro show_list(val) -%}
    <ul class="list-group">
        {% for subval in val %}
            <li class="list-group-item">{{ show_value(subval) }}</li>
        {% endfor %}
    </ul> <!-- list-group -->
{%- endmacro %}

{% macro show_value(val) -%}
    {% if val.items  %}
        {{ show_dict(val, gen_id()) }}
    {% elif val.__iter__ %}
        {{ show_list(val) }}
    {% else %}
        {{ val }}
    {% endif %}
{%- endmacro %}

{% macro show_dict(val, unique, collapsed=True) -%}
    {% if '_href' in val and not '_type' in val %}
        <!-- just a link -->
        <a href={{ val._href }}>{{ val._disp }}</a>
    {% else %}
        <!-- either an embedded resource or normal dict -->
        {% if '_disp' in val %}
            <div class="panel panel-default">
                <div class="panel-heading">
                    <a class="list-group-item-header" href={{ val._href }}>{{ val._disp }}</a>
                    <button type="button" class="btn btn-xs pull-right" data-toggle="collapse" data-target="#{{ unique }}">
                        <span class="caret"></span>
                    </button>
                </div> <!-- panel-heading -->
            {% if collapsed %}
            <ul class="list-group collapse" id="{{ unique }}">
            {% else %}
            <ul class="list-group collapse in" id="{{ unique }}">
            {% endif %}
        {% else %}
            <ul class="list-group">
        {% endif %}
            {% for key, subval in val.items() %}
                {% if key[0] != '_' %}
                    <li class="list-group-item">
                        {{ key }}: {{ show_value(subval) }}
                    </li>
                {% endif %}
            {% endfor %}
        </ul>
        {% if '_disp' in val %}
            </div> <!-- panel -->
        {% endif %}
    {% endif %}
{%- endmacro %}
*/

function render_chart(raw_data, element) {
    $("#chart-header").removeClass("hidden")

    data = []
    for(i = 0; i < raw_data.length; i++) {
        new_point = {
            x: Date.parse(raw_data[i].timestamp) / 1000,
            y: raw_data[i].value
        }
        data.push(new_point)
    };

    //datachart = $("<div/>").id("data-chart");
    //element.append(datachart)
    var graph = new Rickshaw.Graph( {
        element: document.querySelector("#data-chart"),
        // width: 580,
        height: 250,
        series: [ {
            name: 'Value',
            color: 'steelblue',
            data: data
        } ]
    } );
    var xAxis = new Rickshaw.Graph.Axis.Time({
        graph: graph,
        timeFixture: new Rickshaw.Fixtures.Time.Local()
    });
    var yAxis = new Rickshaw.Graph.Axis.Y({graph: graph});
    var hoverDetail = new Rickshaw.Graph.HoverDetail({
        graph: graph,
        xFormatter: function(x) {
            return new Date(x * 1000).toString();
    }});
    graph.render();

    var slider = new Rickshaw.Graph.RangeSlider({
        graph: graph,
        element: document.querySelector('#slider')
    });
}

function render_dict(data, title, element) {
    var attrs_panel = $("<div/>").addClass("panel").addClass("panel-default");
    element.append(attrs_panel);
    if(title !== null) {
        var attrs_title = $("<div/>").addClass("panel-heading").text(title);
        attrs_panel.append(attrs_title);
    }
    var attrs_ul = $("<ul/>").addClass("list-group");
    attrs_panel.append(attrs_ul);
    if(data) {
        $.each(data, function(key, val) {
            if(key != "_links" && key != "_embedded") {
                var cell = $("<li/>").addClass("list-group-item");
                attrs_ul.append(cell);
                cell.append(key + ": ");
                if($.isPlainObject(val)) {
                    render_dict(val, null, cell);
                }
                else if(key != "data") {
                    cell.append(val.toString());
                }
            }
        })
    }
}

function render_response(data, element) {
    links_panel = $("<div/>").addClass("panel").addClass("panel-default");
    element.append(links_panel);

    links_title = $("<div/>").addClass("panel-heading").text("Links");
    links_panel.append(links_title);
    rels_ul = $("<ul/>").addClass("list-group");
    links_panel.append(rels_ul);

    if(data._links) {
        $.each(data._links, function(rel, link) {
            if(rel != "self" && rel != "curies") {
                cell = $("<li/>").addClass("list-group-item");
                rels_ul.append(cell);
                cell.append(rel + ": ");
                if($.isArray(link)) {
                    ul = $("<ul/>").addClass("list-group");
                    cell.append(ul)
                    $.each(link, function(i, link_item) {
                        li = $("<li/>").addClass("list-group-item");
                        ul.append(li)
                        dest_link = $("<a/>").text(link_item.title).attr("href", link_item.href);
                        li.append(dest_link);
                    })
                }
                else {
                    // link is just a link, not a list of links
                    dest_link = $("<a>").text(link.title).attr("href", link.href);
                    cell.append(dest_link);
                }
            }
        })
    }

    render_dict(data, "Attributes", element);
}

function render_form(data, form_element, submit_btn) {
    var form = new JSONEditor(form_element, {
        schema: data,
        theme: 'bootstrap3'
    });
    submit_btn.addEventListener('click', function() {
        // Get the value from the editor
        var errors = form.validate();
        if(errors.length == 0) {
            var form_json = JSON.stringify(form.getValue());
            $.post(window.location.href, form_json, function(data) {
                // redirect to the given page
                window.location.href = data._links.self.href;
            });
        }
        else {
            alert("Form Validation Errors");
        }
    });
}
