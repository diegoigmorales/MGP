local registry = nil

local function load_registry()
  if registry ~= nil then return registry end
  local file = io.open("_generated/registry.json", "r")
  if not file then
    io.stderr:write("No se encontró _generated/registry.json\n")
    registry = { backlinks = {} }
    return registry
  end
  local raw = file:read("*all")
  file:close()
  registry = pandoc.json.decode(raw)
  return registry
end

function Div(div)
  if not div.classes:includes("knowledge-object") then return nil end
  local tag = div.attributes["tag"]
  if not tag then return nil end

  div.content:insert(1, pandoc.Para({
    pandoc.Span({pandoc.Str("TAG " .. tag)}, pandoc.Attr("", {"knowledge-tag"}))
  }))

  local entries = load_registry().backlinks[tag]
  if entries and #entries > 0 then
    local items = {}
    for _, item in ipairs(entries) do
      local label = item.relation .. " · " .. item.tag .. " · " .. item.title
      table.insert(items, {pandoc.Plain({pandoc.Link(label, item.href)})})
    end
    div.content:insert(pandoc.Div({
      pandoc.Para({pandoc.Strong("Referencias inversas")}),
      pandoc.BulletList(items)
    }, pandoc.Attr("", {"knowledge-backlinks"})))
  end
  return div
end
