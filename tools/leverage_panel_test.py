#!/usr/bin/env python3
"""Source-bound checks for the six-metric MT5 cockpit and risk invariants.

These inspect the production MQL5 source. They cannot prove native compilation,
chart rendering, template persistence or clicks in MetaTrader.
"""

from pathlib import Path
from leverage_source import expanded_source
import json
import re


ROOT = Path(__file__).resolve().parents[1]
INDICATOR = ROOT / "mt5/jpw-alavancagem-atual/MQL5/Indicators/JPWealth/JPW_Alavancagem_Atual.mq5"
GENESIS_CORE = ROOT / "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Genesis_Core.mqh"
TERMINAL = ROOT / "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Terminal.mqh"
GENESIS_STORE = ROOT / "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Genesis_Store.mqh"
RAIZ_CORE = ROOT / "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_RaizN_Core.mqh"
RAIZ_STORE = ROOT / "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_RaizN_Store.mqh"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def body_of(source: str, signature: str) -> str:
    """Return one function body, keeping nested MQL blocks intact."""
    start = source.find(signature)
    while start >= 0:
        opening = source.find("{", start + len(signature))
        require(opening >= 0, f"missing body for {signature}")
        terminator = source.find(";", start + len(signature))
        if terminator < 0 or opening < terminator:
            break
        start = source.find(signature, terminator + 1)
    require(start >= 0, f"missing definition for {signature}")
    depth = 0
    for index in range(opening, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[opening + 1:index]
    raise AssertionError(f"unclosed body for {signature}")


def check_typed_presentation(source: str) -> None:
    build = body_of(source, "void JPWBuildPresentation(")
    refresh = body_of(source, "void JPWRefresh()")
    render = body_of(source, "void JPWAcceptCollection(")
    display = body_of(source, "void JPWRenderCurrentDisplay(")
    invalidate = body_of(source, "void JPWInvalidateIdentityPresentation()")
    require("JPWCockpitSnapshot g_cockpit_snapshot;" in source and
            "g_cockpit_snapshot.symbol=_Symbol;" in build and
            "g_cockpit_snapshot.account_key=" in build and
            "g_cockpit_snapshot.sequence=" in build,
            "presentation must bind a measured sample to account and exact symbol")
    for index, title in enumerate(("Leverage", "Floating P/L", "Genesis SL", "Raiz N 1W", "Raiz N 2W", "Stop risk")):
        require(f'JPWViewMetric({index},"{title}"' in build,
                f"missing typed metric card {title}")
    require("JPWViewMetric(2," in build and "g_genesis_quality" in build and
            "JPWViewMetric(3," in build and "g_raiz_quality" in build and
            "JPWViewMetric(4," in build and "g_scale2_quality" in build,
            "metric state must be typed per subsystem, not parsed from Portuguese text")
    require("g_leverage_quality=JPW_VIEW_NA;" in invalidate and
            "g_leverage_quality=JPW_VIEW_CURRENT;" in refresh and
            "g_leverage_quality=(estimated ? JPW_VIEW_ESTIMATED : JPW_VIEW_CURRENT);" in refresh,
            "leverage must distinguish unavailable, current and estimated")
    require("g_panel_value=shown_value;" in render and
            "JPWRenderCurrentDisplay();" in render and
            "JPWBuildPresentation(g_panel_value" in display,
            "presentation must be rebuilt from the visible account reading")
    require("último equity informado pelo terminal" in display,
            "leverage explanation must retain its denominator basis")


def check_account_identity_guard(source: str, render: str) -> None:
    guard = body_of(render, "if(g_account_known &&")
    invalidate = body_of(source, "void JPWInvalidateIdentityPresentation()")
    require("!JPWReadAccount(visible_account)" in render and
            "!JPWAccountsEqual(g_account,visible_account)" in render,
            "render must reject a missing or changed account identity")
    require(render.index("string shown_value=value;") <
            render.index("if(g_account_known &&") <
            render.index("g_panel_value=shown_value;") <
            render.index("JPWRenderCurrentDisplay();"),
            "identity check must run before caching or drawing a prior account value")
    require('shown_value="N/D";' in guard and
            'shown_state="Indisponível — identidade da conta alterada";' in guard and
            'JPWInvalidateIdentityPresentation();' in guard and
            all(f'g_{metric}_quality=JPW_VIEW_NA;' in invalidate for metric in
                ('leverage', 'floating', 'genesis', 'raiz', 'scale2')),
            "a changed account must replace the old leverage reading")
    require('g_floating_line="Floating P/L: N/A";' in invalidate and
            'g_dd_line="DD / saldo: N/D";' in invalidate and
            'g_floating_short="P/L: N/A";' in invalidate and
            'g_dd_short="DD: N/D";' in invalidate and
            'g_genesis_line="Genesis SL: N/A";' in invalidate and
            'g_genesis_short="SL: N/A";' in invalidate and
            'g_raiz_line="Raiz N diag. 1W: N/A";' in invalidate and
            'g_raiz_short="RN1W: N/A";' in invalidate and
            'g_scale2_line="Raiz N diag. 2W: N/A";' in invalidate and
            'g_scale2_short="RN2W: N/A";' in invalidate,
            "a changed account must clear all full and narrow metric readings")
    require("g_floating_tooltip=" in invalidate and "g_dd_tooltip=" in invalidate and
            "g_genesis_tooltip=" in invalidate and "g_raiz_tooltip=" in invalidate and
            "g_scale2_tooltip=" in invalidate and
            "g_panel_status=shown_state;" in render,
            "the changed-account state must reach labels and tooltips")
    require('g_floating_value="N/A"; g_genesis_value="N/A";' in invalidate and
            'g_raiz_value="N/A"; g_scale2_value="N/A";' in invalidate and
            'g_raiz_details_open=false;' in invalidate,
            "account switch must clear typed values and close a stale drilldown")


def check_narrow_chart(hud: str) -> None:
    require('JPWPanelHUDReservedWidth(chart_width,font_height,pad,button_width)' in hud and
            'const int available=width-2*pad;' in hud and
            'TextGetSize(shown[i],measured,text_height)' in hud,
            'content must be measured against reserved HUD geometry')
    require('compact_title[i]+": "+metric.value+" · "+JPWGenetrixMetricQuality(i,metric.quality)' in hud and
            'observer_missing ? "Risk: N/A · Check Observer"' in hud and
            'shown[i]=compact_title[i]+": Cockpit";' in hud and
            'const bool summary=(visible>0 &&' in hud and 'if(summary)' in hud and
            'active=-1' not in hud and 'max_text' not in hud,
            'overflow must keep geometry stable, preserve a named Cockpit route and never cut a value')
    require('if(visible==0)' in hud and 'Open Cockpit' in hud,
            'all-hidden configuration must retain a visible cockpit launcher')
    require('const int font_height=(int)text_height;' in hud and
            'const int header_safe=(font_height*3+10>JPWUIDesignPx(44) ? font_height*3+10 : JPWUIDesignPx(44));' in hud and
            'const int inset_y=(!lower && InpOffsetY<header_safe ? header_safe : InpOffsetY);' in hud,
            'upper HUD must use stable measured text height and a DPI-scaled 44 px reserve below the native instrument heading')
    require('JPWPanelHUD(' in hud and 'const int height=active*row_height+button_height+3*pad;' in hud,
            'all four corners must fit the complete block including its button')


def check_six_labels_and_lifecycle(source: str, render: str) -> None:
    clear=body_of(source,'void JPWClearPanel()')
    hud=body_of(source,'void JPWRenderHUD()')
    init=body_of(source,'int OnInit()')
    orphan_cleanup=body_of(source,'void JPWCockpitRemoveForeignHUD(')
    owned_name=body_of(source,'bool JPWCockpitOwnedUIName(')
    owned_suffix=body_of(source,'bool JPWCockpitOwnedSuffix(')
    event=body_of(source,'void JPWHandleChartEvent(')
    deinit=body_of(source,'void OnDeinit(')
    require('for(int i=0;i<JPW_COCKPIT_METRIC_COUNT;i++)' in hud and 'JPWCockpitVisible(prefs,i)' in hud and
            re.search(r'(?:const\s+)?JPWCockpitMetric metric=g_cockpit_snapshot\.metric\[i\];', hud) and
            'g_panel_count=JPW_COCKPIT_METRIC_COUNT;' in hud,
            'HUD must read six independent typed metrics through visibility bits')
    require('g_dd_line' not in hud and 'JPWMDDObserve' not in hud,
            'DD/MDD must remain off HUD and independent from visibility')
    require('TextGetSize("Mg",measured,text_height)' in hud and
            'const int font_height=(int)text_height;' in hud and
            'const int row_height=font_height+gap;' in hud,
            'HUD spacing must retain the initial measured text height across value measurements')
    require('OBJPROP_CORNER,CORNER_LEFT_UPPER' in hud and
            'OBJPROP_ANCHOR,ANCHOR_LEFT_UPPER' in hud and
            'OBJ_RECTANGLE_LABEL' in hud and 'OBJPROP_BGCOLOR,surface' in hud,
            'labels and contrasting background must use absolute chart coordinates')
    require('ObjectSetString(0,name,OBJPROP_TEXT,shown[i])' in hud and
            'g_cockpit_snapshot.metric[tip_index].reason' in hud and
            'Click for details.' in hud,
            'abbreviated HUD must retain the reason and a route to full details')
    require('ObjectDelete(0,g_panel_prefix+IntegerToString(i))' in clear and
            'StringFormat("JPW_LEV_%I64d_",ChartID())' in init and
            'JPWCockpitRemoveForeignHUD(g_panel_prefix)' in init and
            'ObjectsTotal(0,-1,-1)' in orphan_cleanup and
            'ObjectName(0,i,-1,-1)' in orphan_cleanup and
            'JPWCockpitOwnedUIName(name)' in orphan_cleanup and
            'JPWCockpitOwnedSuffix(suffix)' in orphan_cleanup and
            'const string stem="JPW_LEV_";' in owned_name and
            'const int chart_start=at;' in owned_name and
            all(token in owned_suffix for token in ('HUD_BG', 'RAIZ_DETAILS_BUTTON', 'RAIZ_UI_')) and
            'ObjectDelete(0,name)' in orphan_cleanup and
            'JPW_COCKPIT_PREF_OBJECT' not in orphan_cleanup,
            'stable chart-ID namespace must clean only current-chart UI, not preference')
    require('JPW_COCKPIT_PREF_OBJECT' not in clear and 'JPW_COCKPIT_PREF_OBJECT' not in deinit,
            'detach must leave chart/template preference object intact')
    require('JPWRaizSaveVisibleFields(); JPWRaizPanelDestroy();' in event,
            'resize must save draft before redrawing')
    require('EventKillTimer();' in deinit and 'JPWClearPanel();' in deinit and
            'JPWRaizPanelDestroy();' in deinit and 'IndicatorRelease(g_raiz_atr_handle)' in deinit,
            'detach must release objects, timer and ATR')


def check_same_chart_dialog_cleanup(source: str) -> None:
    """A restored same-chart dialog must not survive indicator initialization."""
    init = body_of(source, 'int OnInit()')
    dialog_destroy = body_of(source, 'void JPWRaizPanelDestroy()')
    require(init.index('g_panel_prefix=StringFormat("JPW_LEV_%I64d_",ChartID());') <
            init.index('JPWCockpitRemoveForeignHUD(g_panel_prefix);') <
            init.index('JPWRaizPanelDestroy();') <
            init.index('JPWCockpitLoadPrefs();'),
            'OnInit must remove transient same-ChartID dialog objects before loading the visual preference')
    require('JPW_COCKPIT_PREF_OBJECT' not in dialog_destroy and
            'g_panel_prefix+"RAIZ_UI_"' in dialog_destroy and
            'ObjectsTotal(0,-1,-1)' in dialog_destroy and
            'ObjectName(0,i,-1,-1)' in dialog_destroy and
            'StringFind(name,owned)==0' in dialog_destroy and
            'ObjectDelete(0,name)' in dialog_destroy,
            'same-chart dialog cleanup must enumerate every RAIZ_UI control, never the preference object')


def check_live_sample_invalidation(source: str) -> None:
    """An early return must not show the last account's quote/ATR in Data Status."""
    collect = body_of(source, 'void JPWCollectRaizN()')
    refresh = body_of(source, 'void JPWRefresh()')
    clear = body_of(source, 'void JPWClearRaizLiveSample(')
    account_change = body_of(refresh, 'if(!g_account_known || !JPWAccountsEqual(g_account,current))')
    for field in ('p0', 'atr', 'distance', 'percent', 'bar_time',
                  'current_bar_time', 'quote_time_msc', 'current', 'reason'):
        require(f'g_live_sample.{field}=' in clear,
                f'live sample reset must clear {field} before a new account reading')
    require(collect.lstrip().startswith('JPWClearRaizLiveSample(') and
            collect.index('JPWClearRaizLiveSample(') < collect.index('JPWRaizNFactorLoad') <
            collect.index('JPWRaizNReadLiveBase'),
            'every Raiz N collection must invalidate the prior quote/ATR before factor or account early returns')
    require('JPWClearRaizLiveSample(' in account_change and
            account_change.index('JPWClearRaizLiveSample(') < account_change.index('g_account=current;'),
            'account switch must clear old quote/ATR before updating the displayed account identity')


def check_cockpit_navigation(source: str) -> None:
    cockpit = body_of(source, 'void JPWRenderCockpit()')
    event = body_of(source, 'void JPWHandleChartEvent(')
    size = re.search(r'JPWPanelCockpit\(chart_width,chart_height,(\d+),(\d+),g_details_rect\)', cockpit)
    # 1.19 names stable route/action IDs while keeping the original semantics.
    required_ids = {"JPW_ROUTE_OVERVIEW":7, "JPW_ROUTE_SETTINGS":10,
                    "JPW_ROUTE_STOPS":11, "JPW_ROUTE_RAIZN":12,
                    "JPW_ROUTE_STOP_ROW":14, "JPW_ACTION_CLOSE":37,
                    "JPW_ACTION_TAB_FIRST":40, "JPW_ACTION_TAB_STOPS":41,
                    "JPW_ACTION_TAB_RAIZN":42, "JPW_ACTION_TAB_SYSTEM":43,
                    "JPW_ACTION_TAB_SETTINGS":44, "JPW_ACTION_TAB_HISTORY":120}
    for name, value in required_ids.items():
        require(re.search(r'\b'+name+r'\s*=\s*'+str(value)+r'\b', source) is not None,
                f'stable route/action identity changed: {name}')
    require(size is not None and int(size[1]) >= 1000 and int(size[2]) >= 700 and
            'if(g_details_rect.height<min_structure || inner<JPWUIDesignPx(110))' in cockpit and
            'JPWRaizCreateButton(JPW_ACTION_CLOSE,"×"' in cockpit and
            'Conta · amplie o gráfico' in cockpit and
            'if(close_height>0 && close_width>0)' in cockpit and
            'OBJPROP_YSIZE,close_height' in cockpit,
            'tiny viewport must retain a reachable bounded close control and readable hint')
    require('g_raiz_tab==JPW_ROUTE_OVERVIEW ? "Visão geral"' in cockpit and
            'g_raiz_tab==JPW_ROUTE_STOPS || g_raiz_tab==JPW_ROUTE_STOP_ROW ? "Stops"' in cockpit and
            'g_raiz_tab==JPW_ROUTE_RAIZN ? "Raiz N"' in cockpit and
            'g_raiz_tab==JPW_ROUTE_SETTINGS ? "Ajustes"' in cockpit and
            'JPWRaizCreateButton(tab_actions[i]' in cockpit and
            'string tabs[6]' in cockpit and 'Histórico Pessoal' in cockpit and
            'const int tab_actions[6]={JPW_ACTION_TAB_FIRST,JPW_ACTION_TAB_STOPS,JPW_ACTION_TAB_RAIZN,' in cockpit and
            'JPW_ACTION_TAB_SYSTEM,JPW_ACTION_TAB_SETTINGS,JPW_ACTION_TAB_HISTORY' in cockpit and
            'JPWUIDesignNavColumns(tabs,6,inner,g_details_font,g_details_pad)' in cockpit,
            'cockpit must retain all six tabs, stable actions and content-measured navigation')
    require('if(id==CHARTEVENT_KEYDOWN && g_raiz_details_open && g_raiz_tab>=JPW_ROUTE_OVERVIEW)' in event and
            'if(!JPWDetailsContextCurrent()) return;' in event and
            'lparam==37 || lparam==39' in event and
            'lparam>=49 && lparam<=55' in event,
            'keyboard navigation must be scoped to current-account cockpit pages')
    require(all(token in event for token in ('"CARD_BG_"+IntegerToString(i)',
            '"CARD_"+IntegerToString(i)+"_VALUE"',
            '"CARD_"+IntegerToString(i)+"_QUALITY"',
            '"CARD_"+IntegerToString(i)+"_REASON"')),
            'clicking a card body, value, quality or reason must open its metric detail')


def check_defaults_and_status_source(source: str) -> None:
    manifest_version = json.loads((ROOT / "downloads/jpw-alavancagem-atual/manifest.json").read_text())['version']
    require(re.search(r'#property version\s+JPW_PRODUCT_MQL_VERSION\b', source) and
            re.search(r'#define JPW_PRODUCT_MQL_VERSION "[0-9]+\.[0-9]+"', source),
            "MQL property must use central version metadata")
    require('JPW_PRODUCT_NAME+" · Cockpit "+JPW_PRODUCT_VERSION' in source and
            f'#define JPW_PRODUCT_VERSION "{manifest_version}"' in source,
            "short name and central version must match the package manifest")
    require("input int InpFontSize=8;" in source and "input int InpOffsetX=16;" in source and
            "input int InpOffsetY=40;" in source,
            "compact default size or placement changed")
    require("input color InpFontColor=C'118,118,118';" in source, "default label must remain gray")
    require("input long InpGenesisTicket=0;" in source and
            'input string InpPipSymbol="";' in source and
            "input double InpPipSize=0.0;" in source,
            "Genesis ticket and exact-symbol pip opt-in must retain safe defaults")
    refresh = body_of(source, "void JPWRefresh()")
    require('state="Atual";' in refresh and '"Estimativa — sem conexão"' in refresh,
            "refresh must distinguish current readings and estimates")
    require('" | Cotação mais antiga: "' in refresh and
            '" | Base: último equity informado pelo terminal"' in refresh,
            "refresh must supply quote age and equity basis to the tooltip")
    require('JPWAcceptCollection("N/D","Indisponível — "+JPWErrorText(status))' in refresh,
            "calculation failures must replace the previous numeric reading")


def check_account_metrics_source(source: str, render: str) -> None:
    collect = body_of(source, "bool JPWCollectAccountMetrics(")
    refresh = body_of(source, "void JPWRefresh()")
    unavailable = body_of(source, "void JPWMetricUnavailable(")
    for property_name in ("ACCOUNT_BALANCE", "ACCOUNT_EQUITY", "ACCOUNT_PROFIT", "ACCOUNT_CREDIT"):
        require(f"JPWReadAccountMetric({property_name}," in collect,
                f"account sample lost {property_name}")
    require("JPWAccountsEqual(account,after)" in collect and
            "JPWReadAccountMetric(ACCOUNT_BALANCE,checked_balance)" in collect and
            "JPWReadAccountMetric(ACCOUNT_CREDIT,checked_credit)" in collect,
            "account, balance and credit context must be rechecked")
    require("for(int attempt=0;attempt<2;attempt++)" in collect and
            "if(attempt==0 && JPWWithinBudget(started)) continue;" in collect,
            "changed context must retry only within the existing budget")
    require("if(have_profit && JPWFloatingPercent(balance,profit,floating))" in collect and
            "if(have_equity && JPWBalanceDDPercent(balance,equity,dd))" in collect,
            "floating and DD must use independent inputs and pure functions")
    require(re.search(r'const bool estimated=\s*!connected\s*\|\|\s*!clock_valid\s*\|\|\s*!have_credit;',
                      collect) and
            '" · Estimated"' in collect and '"Current"' in collect,
            "metric quality must cover connection, time and credit context independently of FX routes")
    require('g_floating_line="Floating P/L: N/A";' in unavailable and
            'g_dd_line="DD / saldo: N/D";' in unavailable,
            "invalid metrics must display N/D instead of a previous or false zero")
    require(refresh.index("JPWCollectAccountMetrics(current,connected,clock_valid)") <
            refresh.index("JPWAccountUnits(current.currency,currency,divisor)") <
            refresh.index("JPWCollectReading(before,current,currency"),
            "account percentages must be collected before notional conversion")
    require("if(!estimated && observed_at>0 && JPWWithinBudget(started))" in collect and
            "JPWMDDObserve(account,balance,equity,dd," in collect,
            "only current valid DD can update the observed maximum")
    require("const string percent=JPWFormatPercent(dd,false);" in collect and
            'g_dd_line="DD / saldo: "+percent+suffix;' in collect,
            "DD line must display the current deficit percentage")
    require("JPWMDDObserve" not in render and "confirmed." not in render,
            "observed maximum must remain off the chart")
    visible_assignments = re.findall(r'g_(?:floating|dd)_line\s*=\s*(.+?);', collect)
    require(visible_assignments and all("max" not in text.lower() and "mdd" not in text.lower()
                                        for text in visible_assignments),
            "metric lines must not reveal the persisted maximum")


def check_genesis_source(source: str, render: str) -> None:
    core = GENESIS_CORE.read_text(encoding="utf-8")
    terminal = TERMINAL.read_text(encoding="utf-8")
    store = GENESIS_STORE.read_text(encoding="utf-8")
    select = body_of(core, "JPW_GENESIS_SELECTION JPWGenesisSelect(")
    distance = body_of(core, "JPW_GENESIS_DISTANCE JPWGenesisDistance(")
    collector = body_of(source, "void JPWCollectGenesis(")
    unavailable = body_of(source, "void JPWGenesisUnavailable(")

    require(all(token not in core for token in
                ("AccountInfo", "PositionGet", "FileOpen", "OrderSend", "ChartGet")),
            "Genesis selection and mathematics must stay pure")
    require("positions[i].symbol!=symbol || positions[i].direction!=direction" in select and
            "positions[i].opened_msc<oldest_time" in select and "tie=true;" in select and
            "requested_ticket>0" in select,
            "automatic selection needs one exact group and one unique oldest timestamp")
    require("JPWGenesisFindByIdentifier" in core and
            "positions[i].identifier!=identifier" in core,
            "saved identifier must locate the existing reference, never pick a successor")
    require("direction==POSITION_TYPE_BUY ? bid : ask" in distance and
            "direction==POSITION_TYPE_BUY ? price-sl : sl-price" in distance and
            "const double tolerance=tick_size*1e-8;" in distance and
            "JPW_GENESIS_DISTANCE_REACHED" in distance and
            "JPW_GENESIS_DISTANCE_PASSED" in distance,
            "distance must use closing Bid/Ask, signed D and sub-tick zero tolerance")
    require("pip_symbol==symbol" in distance and "pip_size>=point" in distance,
            "pips must require an explicit exact-symbol unit")

    snapshot = body_of(terminal, "bool JPWReadGenesisSnapshot(")
    equality = body_of(terminal, "bool JPWGenesisSnapshotsEqual(")
    require(all(token in snapshot for token in
                ("POSITION_IDENTIFIER", "POSITION_TIME_MSC", "POSITION_SL",
                 "POSITION_TIME_UPDATE_MSC", "POSITION_VOLUME", "PositionSelectByTicket")),
            "terminal snapshot must freshly collect reference identity, SL and context")
    require(all(token in equality for token in
                ("opened_msc", "updated_msc", "sl", "volume", "direction", "identifier")),
            "before/after snapshot must detect changes relevant to the reference")
    require("JPWReadGenesisSnapshot(before)" in collector and
            "JPWReadGenesisSnapshot(after)" in collector and
            "JPWGenesisSnapshotsEqual(before,after)" in collector and
            "JPWAccountsEqual(account,later)" in collector,
            "Genesis must use a coherent current-account snapshot")
    require("JPWGenesisRead(account,InpGenesisTicket" in collector and
            "JPWGenesisCreate(account,InpGenesisTicket" in collector and
            "JPWGenesisFindByIdentifier(before,saved.identifier,candidate)" in collector,
            "Genesis must persist and resume its own reference identity")
    absence = collector.split("if(!found && stored==JPW_GENESIS_VALID)", 1)[1].split(
        "// The saved identifier anchors", 1)[0]
    require("JPWGenesisTransition(" not in collector and
            "encerramento não comprovado" in absence and
            "referência não localizada" in absence,
            "local absence must remain indeterminate without a position synchronization witness")
    require("JPW_GENESIS_FOLDER" in store and "genesis_" in store and
            "JPW_MDD_FOLDER" not in store and "JPWMDDObserve" not in collector,
            "Genesis records must stay separate from MDD")
    refresh = body_of(source, "void JPWRefresh()")
    require("g_genesis_due=true" in refresh and
            "g_genesis_refresh_started=g_cycle_started_ms" in refresh and
            "JPWCollectGenesis(g_genesis_refresh_account" in render,
            "Genesis line must be collected independently after financial metrics")
    require('g_genesis_line="Genesis SL: N/A";' in unavailable and
            '+reason+' in unavailable, 'unavailable reason belongs in complete tooltip')
    require('"Position SL" : "Genesis SL"' in collector and
            'g_genesis_line=basis+": "+(current ? "" : "≈")+pct+suffix;' in collector,
            'Genesis must be percent-first and distinguish netting aggregate')
    require(all(state in collector for state in (': No SL', ': SL reached', ': SL passed')) and
            '"Inferred" : "Selected"' in collector and '" · Netting"' in collector,
            'short English states must preserve provenance and netting')
    invalidate = body_of(source, "void JPWInvalidateIdentityPresentation()")
    require("g_genesis_line" in invalidate and "g_genesis_tooltip" in invalidate and
            "JPWMDDObserve" not in collector,
            "Genesis presentation must not interfere with MDD persistence")


def check_raiz_n_source(source: str, render: str) -> None:
    core = RAIZ_CORE.read_text(encoding="utf-8")
    store = RAIZ_STORE.read_text(encoding="utf-8")
    calculate = body_of(core, "JPW_RAIZN_RESULT JPWRaizNCalculate(")
    native_atr = body_of(source, "bool JPWRaizNativeATR(")
    apply = body_of(source, "void JPWRaizApply()")
    bind = body_of(source, "void JPWRaizBindTicket()")
    collect = body_of(source, "void JPWCollectRaizScenario()")
    event = body_of(source, "void JPWHandleChartEvent(")
    require(all(token not in core for token in
                ("AccountInfo", "PositionGet", "FileOpen", "OrderSend", "ChartGet")),
            "Raiz N math must remain pure")
    require("MathSqrt((double)n)" in calculate and
            "100.0*ratio" in calculate and "scaled_atr*f" in calculate,
            "Raiz N must calculate price distance and percentage separately")
    require("PERIOD_H4" in native_atr and "CopyTime(" in native_atr and
            "CopyBuffer(" in native_atr and "JPWRaizNBarClosedBy" in native_atr and
            "SERIES_SYNCHRONIZED" in native_atr and "EMPTY_VALUE" in native_atr,
            "MT5 ATR must use an observed closed H4 bar without future data")
    require("JPWRaizNReadActive" in collect and "JPWRaizNCalculate" in collect and
            "g_saved_raiz_line=\"Raiz N: \"+percent" in collect and
            "JPWMDDObserve" not in collect,
            "Raiz N display must read its own scenario and remain independent")
    require("JPWRaizNConfirm" in apply and "expected" in apply and
            "JPWAccountsEqual(account,after)" in apply and
            "JPWRaizNBind" not in apply,
            "Apply must confirm a scenario atomically without implicit binding")
    require("JPWReadGenesisSnapshot(first)" in bind and
            "JPWGenesisSnapshotsEqual(first,second)" in bind and
            "chosen.symbol!=_Symbol" in bind and "JPWRaizNBind" in bind,
            "explicit ticket binding must verify the current position")
    require("CHARTEVENT_OBJECT_ENDEDIT" in event and
            "JPWRaizApply()" in event and "JPWRaizBindTicket()" in event and
            "JPWRaizPanelDestroy()" in event,
            "details panel must support edit, Apply and Cancel")
    require("raiz_n_v1" in store and "JPW_RAIZN_FOLDER" in store and
            "JPWMDDObserve" not in store and "JPWGenesisCreate" not in store,
            "Raiz N persistence must remain separate from MDD and Genesis")
    require("iATR(_Symbol,PERIOD_H4,55)" in source and
            "IndicatorRelease(g_raiz_atr_handle)" in source,
            "ATR handle must be reused and released")


def check_live_config_and_details(source: str) -> None:
    collect=body_of(source,'void JPWCollectRaizN()')
    refresh=body_of(source,'void JPWRefresh()')
    reset_tick=body_of(source,'void JPWHorizonResetTickEvidence()')
    apply=body_of(source,'void JPWLiveApply()')
    factor_apply=body_of(source,'void JPWFactorApply()')
    event=body_of(source,'void JPWHandleChartEvent(')
    details=body_of(source,'void JPWRenderRaizDetails()')
    read=body_of(source,'void JPWDetailsReadMDD()')
    observer=body_of(source,'void JPWDetailsReadObserver()')
    require('JPWRaizNConfigLoad' in collect and 'JPWRaizNFactorLoad' in collect and
            'JPWRaizNReadLiveBase' in collect and 'JPWHorizonResolve' in collect and
            collect.count('JPWRaizNCalculate(g_live_sample.p0,g_live_sample.atr,')==2 and
            'Raiz N diag. 1W:' in collect and 'Raiz N diag. 2W:' in collect,
            'automatic horizons must apply selected F to one raw quote/ATR sample without legacy N/F')
    require('g_horizon_new_tick' in collect and 'JPW_HORIZON_EXACT' in collect and
            'P-21 permanece PENDING' in collect,
            'Current needs target-symbol freshness and approved calendar, not factor approval')
    require('g_factor_state!=JPW_RAIZN_VALID && g_factor_state!=JPW_RAIZN_ABSENT' in collect and
            collect.index('JPWRaizNFactorLoad') < collect.index('JPWRaizNReadLiveBase') and
            'g_factor_preference.factor : JPW_RAIZN_FACTOR_DEFAULT' in collect,
            'an absent factor can default to 1.5, but corrupt/unreadable preference must fail closed')
    connection_change=body_of(refresh,'if(g_connected!=connected)')
    require('JPWHorizonResetTickEvidence()' in connection_change and
            refresh.index('if(g_connected!=connected)') < refresh.index('JPWReadAccount(current)') and
            'g_horizon_new_tick=false;' in reset_tick and
            'SymbolInfoTick(_Symbol,tick)' in reset_tick,
            'reconnection must discard old tick evidence before any failed collection can return')
    require('JPWRaizNConfigSave' not in collect and 'JPWRaizNConfirm' not in collect,
            'timer must not persist settings or rewrite declared scenarios')
    require('PositionsTotal' not in collect and 'JPWReadGenesisSnapshot' not in collect,
            'live diagnostic cannot depend on positions or Genesis')
    require('JPWRaizNConfigSave(JPW_RAIZN_FOLDER,key,_Symbol,g_live_draft_generation' in apply and
            'JPWAccountsEqual(account,g_raiz_draft_account)' in apply,
            'Apply must compare expected generation and draft identity')
    require('JPWRaizPositiveInteger' in apply and 'JPWLivePositiveFactor' in apply and
            'JPWRaizHasText(g_raiz_fields[18])' in apply and
            'JPWRaizHasText(g_raiz_fields[20])' in apply,
            'N/F and both reasons must be explicit')
    require('JPWRaizNFactorSave(JPW_RAIZN_FOLDER,key,_Symbol,' in factor_apply and
            'g_factor_draft_generation,draft,reason' in factor_apply and
            'JPWAccountsEqual(account,g_raiz_draft_account)' in factor_apply and
            'JPWRaizNFactorAllowed(g_factor_draft)' in factor_apply,
            'F Apply must use the separate CAS store and bind account, symbol, and allowed choice')
    close=event.split('if(sparam==JPWRaizUI("BUTTON_5"))',1)[1]
    require('JPWLiveApply' not in close and 'JPWFactorApply' not in close and
            'ConfigSave' not in close and 'FactorSave' not in close,
            'Cancel must not save either settings store')
    require('JPWMDDReadOnly' in read and 'JPWMDDConfirmAccount' in read and
            'ObjectCreate' not in read and 'JPWMDDObserve' not in read,
            'MDD is read-only and lock-released before the dialog is drawn')
    require('JPWObserverReadCurrent' in observer and 'JPWObserverAccountKey' in observer and
            'JPWAccountsEqual(before,after)' in observer and
            'não comprova posição aberta' in observer and 'ObjectCreate' not in observer,
            'observer snapshot must be read-only and cannot certify open positions or Genesis')
    require('JPWPanelDialog' in details and 'JPWPanelPageCount' in details and
            'g_details_rect.compact' in details and 'g_dd_line' in details,
            'Details must use measured viewport pagination and show retained DD')
    require('JPWRaizNNoTouchProbability' in details and
            'Primeiro não toque teórico' in details and
            'OBJPROP_TOOLTIP,"\\n"' in details,
            'Details must show qualified ideal probability without a covering summary tooltip')
    for fn in ('bool JPWRaizCreateLabel','bool JPWRaizCreateEdit','bool JPWRaizCreateButton'):
        body=body_of(source,fn)
        require('OBJPROP_CORNER,CORNER_LEFT_UPPER' in body and 'CORNER_RIGHT_UPPER' not in body,
                'fixed controls must use absolute top-left coordinates')
    require('!g_details_rect.compact && g_raiz_tab<=3' in details and
            'content_height>0 && !g_details_rect.compact' in details,
            'compact chrome must not overlap content with action/footer rows')


def main() -> None:
    source = expanded_source(INDICATOR)
    raw_source = source
    # Legacy routes retain their numeric protocol; naming them must not remove
    # the existing characterization of legacy edit/navigation paths.
    for name, value in re.findall(r"(JPW_(?:ROUTE|ACTION)_\w+)=(\d+)", source):
        source = re.sub(r"\b" + name + r"\b", value, source)
    source = re.sub(r"JPWActionObject\((\d+)\)", lambda m: 'JPWRaizUI("BUTTON_' + m.group(1) + '")', source)
    render = body_of(source, "void JPWAcceptCollection(")
    check_typed_presentation(source)
    check_account_identity_guard(source, render)
    check_narrow_chart(body_of(source, "void JPWRenderHUD()"))
    check_six_labels_and_lifecycle(source, render)
    check_same_chart_dialog_cleanup(source)
    check_live_sample_invalidation(source)
    check_cockpit_navigation(raw_source)
    check_defaults_and_status_source(source)
    check_account_metrics_source(source, render)
    check_genesis_source(source, render)
    check_raiz_n_source(source, render)
    check_live_config_and_details(source)
    print("LEVERAGE COCKPIT SAFETY OK — six typed metrics, isolated calculations and fail-closed visual preference")


if __name__ == "__main__":
    import sys
    from leverage_host_layout import panel
    raise SystemExit(panel(sys.modules[__name__]))
