from __future__ import annotations

import argparse
import json
import logging
import sys
from collections import Counter
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a daily news DOCX report.")
    parser.add_argument(
        "backfill_date",
        nargs="?",
        help="Optional target news date for manual backfill, in YYYY-MM-DD format.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Collect and score items without writing the final DOCX.")
    parser.add_argument("--date", dest="date_option", type=str, help="Target news date in YYYY-MM-DD format.")
    parser.add_argument("--overwrite", action="store_true", help="Allow overwriting an existing output DOCX.")
    parser.add_argument("--check-sources", action="store_true", help="Check every configured source and print item counts.")
    parser.add_argument("--debug-keyword", type=str, help="Print diagnostics for raw/filtered/selected items matching a keyword.")
    parser.add_argument("--probe-domestic-sources", action="store_true", help="Probe domestic source coverage for the target date.")
    parser.add_argument("--probe-international-sources", action="store_true", help="Probe international source coverage for the target date.")
    args = parser.parse_args()
    if args.backfill_date and args.date_option:
        parser.error("Use either positional YYYY-MM-DD or --date YYYY-MM-DD, not both.")
    return args


def main() -> int:
    args = parse_args()

    from src.collect import check_sources, collect_news, probe_domestic_sources, probe_international_sources
    from src.dedupe import dedupe_items_with_report
    from src.links import validate_items_links
    from src.quality import filter_quality_items_with_report
    from src.rank import rank_items, select_top_items, summarize_selection
    from src.render_docx import render_daily_docx
    from src.summary import enrich_items_with_summary_zh, get_summary_runtime
    from src.utils import (
        build_snapshot_path,
        ensure_directory,
        get_target_date,
        load_runtime_config,
        setup_logging,
    )

    config = load_runtime_config()
    summary_runtime = get_summary_runtime(config)
    ensure_directory(Path(config["temp_output_dir"]))
    ensure_directory(Path(config["output_dir"]))
    ensure_directory(Path(config["log_file"]).parent)
    setup_logging(Path(config["log_file"]))

    try:
        target_date = get_target_date(args.date_option or args.backfill_date, config["timezone"])
    except ValueError as exc:
        logging.error("Invalid --date value: %s", exc)
        return 2

    if args.check_sources:
        results = check_sources(config=config, target_date=target_date)
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return 0

    if args.probe_domestic_sources:
        results = probe_domestic_sources(config=config, target_date=target_date)
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return 0

    if args.probe_international_sources:
        results = probe_international_sources(config=config, target_date=target_date)
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return 0

    logging.info("Starting daily news run for target date %s", target_date.isoformat())
    collected_items = collect_news(config=config, target_date=target_date)
    logging.info("Collected %s raw items", len(collected_items))
    diagnostics = {
        "domestic": _section_diagnostics(collected_items, target_date, "domestic"),
        "international": _section_diagnostics(collected_items, target_date, "international"),
    }

    quality_items, exclusion_stats, excluded_watchlist = filter_quality_items_with_report(
        collected_items,
        target_date=target_date,
        config=config,
    )
    logging.info("Excluded non-target-date items: %s", exclusion_stats.get("non_target_date", 0))
    logging.info("Excluded missing-date items: %s", exclusion_stats.get("missing_date", 0))
    logging.info("Excluded future-date items: %s", exclusion_stats.get("future_date", 0))
    logging.info("Excluded roundup/newsletter items: %s", exclusion_stats.get("roundup_newsletter", 0))
    logging.info("Excluded soft-news items: %s", exclusion_stats.get("soft_news", 0))

    deduped_items, dedupe_report = dedupe_items_with_report(quality_items)
    logging.info("Retained %s target-date quality items after deduplication", len(deduped_items))
    logging.info("Deduped by exact URL: %s", dedupe_report["stats"].get("exact_url", 0))
    logging.info("Deduped by title similarity: %s", dedupe_report["stats"].get("title_similarity", 0))
    logging.info("Deduped by event fingerprint: %s", dedupe_report["stats"].get("event_fingerprint", 0))
    logging.info("Deduped by fuzzy event similarity: %s", dedupe_report["stats"].get("fuzzy_event_similarity", 0))

    ranked_items = rank_items(deduped_items, config=config, target_date=target_date)
    domestic_items, international_items, rank_selection_diagnostics = select_top_items(ranked_items, limit=10)
    validate_items_links(domestic_items + international_items)
    enrich_items_with_summary_zh(domestic_items, config=config)
    enrich_items_with_summary_zh(international_items, config=config)
    domestic_summary = summarize_selection(domestic_items)
    international_summary = summarize_selection(international_items)
    source_coverage = _source_coverage_diagnostics(collected_items, quality_items, domestic_items + international_items, target_date)
    selection_diagnostics = {
        "domestic": _selection_diagnostics(ranked_items, domestic_items, "domestic"),
        "international": _selection_diagnostics(ranked_items, international_items, "international"),
    }
    selection_diagnostics["domestic"].update(rank_selection_diagnostics.get("domestic", {}))
    selection_diagnostics["international"].update(rank_selection_diagnostics.get("international", {}))
    duplicate_event_groups = _duplicate_event_groups(quality_items, "international")
    summary_validation_stats = _summary_validation_stats(international_items)
    if len(domestic_items) < 10:
        logging.warning(
            "Domestic high-quality target-date items below target: %s/10",
            len(domestic_items),
        )
    if len(international_items) < 10:
        logging.warning(
            "International high-quality target-date items below target: %s/10",
            len(international_items),
        )

    snapshot_path = build_snapshot_path(Path(config["temp_output_dir"]), target_date)
    duplicates_path = Path(config["temp_output_dir"]) / f"{target_date.isoformat()}_duplicates.json"
    snapshot_payload = {
        "target_date": target_date.isoformat(),
        "domestic_count": len(domestic_items),
        "international_count": len(international_items),
        "domestic_items": domestic_items,
        "international_items": international_items,
        "domestic_summary": domestic_summary,
        "international_summary": international_summary,
        "exclusion_stats": exclusion_stats,
        "diagnostics": diagnostics,
        "source_coverage": source_coverage,
        "selection_diagnostics": selection_diagnostics,
        "duplicate_event_groups": duplicate_event_groups,
        "summary_validation_stats": summary_validation_stats,
        "summary_runtime": summary_runtime,
        "dedupe_stats": dedupe_report["stats"],
        "duplicates_path": str(duplicates_path),
        "watchlist_excluded": excluded_watchlist,
    }
    snapshot_path.write_text(json.dumps(snapshot_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    duplicates_path.write_text(json.dumps(dedupe_report["duplicates"], ensure_ascii=False, indent=2), encoding="utf-8")
    logging.info("Wrote snapshot to %s", snapshot_path)
    logging.info("Wrote duplicates report to %s", duplicates_path)

    if args.debug_keyword:
        _print_debug_keyword(
            keyword=args.debug_keyword,
            raw_items=collected_items,
            quality_items=quality_items,
            selected_items=domestic_items + international_items,
            excluded_watchlist=excluded_watchlist,
        )
        return 0

    if args.dry_run:
        print(f"Target date: {target_date.isoformat()}")
        print(f"LLM summary enabled: {str(summary_runtime['llm_summary_enabled']).lower()}")
        print(f"LLM provider detected: {summary_runtime['provider_detected']}")
        print(f"Summary mode: {summary_runtime['summary_mode']}")
        if not summary_runtime["llm_summary_enabled"]:
            print(f"If false: reason = {summary_runtime['reason']}")
        print(f"Collected raw items: {len(collected_items)}")
        print(f"Excluded non-target-date items: {exclusion_stats.get('non_target_date', 0)}")
        print(f"Excluded missing-date items: {exclusion_stats.get('missing_date', 0)}")
        print(f"Excluded future-date items: {exclusion_stats.get('future_date', 0)}")
        print(f"Excluded roundup/newsletter items: {exclusion_stats.get('roundup_newsletter', 0)}")
        print(f"Excluded soft-news items: {exclusion_stats.get('soft_news', 0)}")
        print(f"Domestic RSS raw items: {diagnostics['domestic']['rss_raw']}")
        print(f"Domestic topic RSS raw items: {diagnostics['domestic']['topic_rss_raw']}")
        print(f"Domestic RSS target-date items: {diagnostics['domestic']['rss_target_date']}")
        print(f"Domestic HTML raw items: {diagnostics['domestic']['html_raw']}")
        print(f"Domestic HTML target-date items: {diagnostics['domestic']['html_target_date']}")
        print(f"Domestic target-date items before quality filter: {diagnostics['domestic']['target_date_before_quality']}")
        print(f"Domestic excluded non-target-date: {exclusion_stats.get('domestic_non_target_date', 0)}")
        print(f"Domestic excluded missing-date: {exclusion_stats.get('domestic_missing_date', 0)}")
        print(f"Domestic excluded soft-news: {exclusion_stats.get('domestic_soft_news', 0)}")
        print(f"Domestic excluded roundup/newsletter: {exclusion_stats.get('domestic_roundup_newsletter', 0)}")
        print(f"Domestic retained after quality filters: {sum(1 for item in quality_items if item.get('section') == 'domestic')}")
        print(f"International RSS raw items: {diagnostics['international']['rss_raw']}")
        print(f"International topic RSS raw items: {diagnostics['international']['topic_rss_raw']}")
        print(f"International RSS target-date items: {diagnostics['international']['rss_target_date']}")
        print(f"International HTML raw items: {diagnostics['international']['html_raw']}")
        print(f"International HTML target-date items: {diagnostics['international']['html_target_date']}")
        print(f"International target-date items before quality filter: {diagnostics['international']['target_date_before_quality']}")
        print(f"International excluded non-target-date: {exclusion_stats.get('international_non_target_date', 0)}")
        print(f"International excluded missing-date: {exclusion_stats.get('international_missing_date', 0)}")
        print(f"International excluded soft-news: {exclusion_stats.get('international_soft_news', 0)}")
        print(f"International excluded roundup/newsletter: {exclusion_stats.get('international_roundup_newsletter', 0)}")
        print(f"Excluded general political sanctions: {exclusion_stats.get('international_general_political_sanctions', 0)}")
        print(f"Excluded explainer/history/background: {exclusion_stats.get('international_explainer_history_background', 0)}")
        print(f"Excluded broker/trading platform items: {exclusion_stats.get('international_excluded_broker_trading_platform', 0)}")
        print(f"Excluded low-quality finance items: {exclusion_stats.get('international_excluded_low_quality_finance', 0)}")
        print(f"Excluded unknown source items: {exclusion_stats.get('international_excluded_unknown_source', 0)}")
        print(f"International retained after quality filters: {sum(1 for item in quality_items if item.get('section') == 'international')}")
        print(f"Watchlist candidate items: {exclusion_stats.get('watchlist_candidates', 0)}")
        print(f"Watchlist items excluded: {exclusion_stats.get('watchlist_excluded', 0)}")
        print(f"Retained target-date quality items after dedupe: {len(deduped_items)}")
        print(f"Deduped by exact URL: {dedupe_report['stats'].get('exact_url', 0)}")
        print(f"Deduped by title similarity: {dedupe_report['stats'].get('title_similarity', 0)}")
        print(f"Deduped by event fingerprint: {dedupe_report['stats'].get('event_fingerprint', 0)}")
        print(f"Deduped by fuzzy event similarity: {dedupe_report['stats'].get('fuzzy_event_similarity', 0)}")
        print(f"International unknown-source backfill added: {exclusion_stats.get('international_unknown_backfill_added', 0)}")
        print(f"Domestic top count: {len(domestic_items)}")
        print(f"International top count: {len(international_items)}")
        print("\nDomestic source coverage:")
        print(json.dumps(source_coverage["domestic"], ensure_ascii=False, indent=2))
        if len(domestic_items) < 8:
            print(f"Domestic shortage reason: {source_coverage['domestic_shortage_reason']}")
        print("\nInternational source coverage:")
        print(json.dumps(source_coverage["international"], ensure_ascii=False, indent=2))
        if len(international_items) < 8:
            print(f"International shortage reason: {source_coverage['international_shortage_reason']}")
        print("\nTop domestic preview:")
        _print_preview(domestic_items)
        print("\nTop international preview:")
        _print_preview(international_items)
        print("\nDomestic category_bucket summary:")
        print(json.dumps(domestic_summary["category_buckets"], ensure_ascii=False, indent=2))
        print("Domestic source summary:")
        print(json.dumps(domestic_summary["sources"], ensure_ascii=False, indent=2))
        print("\nInternational category_bucket summary:")
        print(json.dumps(international_summary["category_buckets"], ensure_ascii=False, indent=2))
        print("International source summary:")
        print(json.dumps(international_summary["sources"], ensure_ascii=False, indent=2))
        print("Selected source_quality summary:")
        print(json.dumps(_source_quality_summary(international_items), ensure_ascii=False, indent=2))
        print("\nDomestic selection diagnostics:")
        print(json.dumps(selection_diagnostics["domestic"], ensure_ascii=False, indent=2))
        print("International selection diagnostics:")
        print(json.dumps(selection_diagnostics["international"], ensure_ascii=False, indent=2))
        print("\nDuplicate event groups:")
        print(json.dumps(duplicate_event_groups, ensure_ascii=False, indent=2))
        print("\nSummary validation stats:")
        print(json.dumps(summary_validation_stats, ensure_ascii=False, indent=2))
        print(f"Snapshot: {snapshot_path}")
        print(f"Duplicates: {duplicates_path}")
        if dedupe_report["examples"]:
            print("\nDedupe examples:")
            for example in dedupe_report["examples"][:5]:
                print(
                    "Dropped duplicate: "
                    f"dropped_title={example['dropped']['title']} | "
                    f"kept_title={example['kept']['title']} | "
                    f"reason={example['reason']} | fingerprint={example['fingerprint']}"
                )
        if excluded_watchlist:
            print("\nExcluded watchlist examples:")
            for item in excluded_watchlist[:5]:
                print(
                    f"title={item.get('title')} | source={item.get('source')} | "
                    f"reason={item.get('exclusion_reason')} | raw_pubdate={item.get('raw_pubdate')} | "
                    f"source_timezone_date={item.get('source_timezone_date')} | "
                    f"target_timezone_date={item.get('target_timezone_date')} | url={item.get('url')}"
                )
        return 0

    output_path = render_daily_docx(
        config=config,
        target_date=target_date,
        domestic_items=domestic_items,
        international_items=international_items,
        overwrite=args.overwrite,
    )
    logging.info("Generated DOCX at %s", output_path)
    print(output_path)
    return 0


def _print_preview(items: list[dict]) -> None:
    for index, item in enumerate(items[:10], start=1):
        tags = ", ".join(item.get("tags", []))
        print(
            f"{index}. [{item.get('source')}] {item.get('published_date') or '未标明'} | "
            f"group={item.get('source_group')} | original_pubdate={item.get('original_pubdate')} | "
            f"{item.get('title')} | original_url={item.get('original_url')} | "
            f"normalized_url={item.get('normalized_url')} | final_url_used={item.get('final_url_used')} | "
            f"link_status={item.get('link_status')} | link_note={item.get('link_note')} | "
            f"final_score={item.get('final_score', item.get('score'))} | "
            f"economic_relevance_score={item.get('economic_relevance_score')} | "
            f"market_impact_score={item.get('market_impact_score')} | "
            f"trade_commodity_score={item.get('trade_commodity_score')} | "
            f"quality_score={item.get('quality_score')} | tags={tags} | "
            f"source_quality={item.get('source_quality')} | date={item.get('published_date')} | "
            f"bucket={item.get('category_bucket')} | summary_zh={item.get('summary_zh')} | "
            f"summary_source={item.get('summary_source')} | summary_confidence={item.get('summary_confidence')} | "
            f"summary_validation={item.get('summary_validation')} | summary_mode={item.get('summary_mode')} | "
            f"summary_reason={item.get('summary_reason')} | bad_summary_reason={item.get('bad_summary_reason')} | "
            f"event_fingerprint={item.get('event_fingerprint')} | duplicate_group_id={item.get('duplicate_group_id')} | "
            f"reason={item.get('reason')}"
        )


def _section_diagnostics(items: list[dict], target_date, section: str) -> dict[str, int]:
    diagnostics = {
        "rss_raw": 0,
        "topic_rss_raw": 0,
        "rss_target_date": 0,
        "html_raw": 0,
        "html_target_date": 0,
        "target_date_before_quality": 0,
    }
    target_date_str = target_date.isoformat()
    for item in items:
        if item.get("section") != section:
            continue
        method = item.get("method") or ""
        is_topic = method in {"google_news_rss", "bing_news_rss"}
        is_rss = method.startswith("rss") or is_topic
        raw_key = "rss_raw" if is_rss else "html_raw"
        target_key = "rss_target_date" if is_rss else "html_target_date"
        diagnostics[raw_key] += 1
        if is_topic:
            diagnostics["topic_rss_raw"] += 1
        if item.get("published_date") == target_date_str:
            diagnostics[target_key] += 1
            diagnostics["target_date_before_quality"] += 1
    return diagnostics


def _selection_diagnostics(ranked_items: list[dict], selected_items: list[dict], section: str) -> dict:
    section_ranked = [item for item in ranked_items if item.get("section") == section]
    section_selected = [item for item in selected_items if item.get("section") == section]
    available_buckets = dict(Counter(item.get("category_bucket", "unknown") for item in section_ranked))
    selected_buckets = dict(Counter(item.get("category_bucket", "unknown") for item in section_selected))
    selected_source_groups = dict(Counter(item.get("source_group", "unknown") for item in section_selected))
    top_titles = [item.get("title") for item in section_selected[:5]]
    return {
        "available_bucket_counts": available_buckets,
        "selected_bucket_counts": selected_buckets,
        "selected_source_groups": selected_source_groups,
        "selected_top_titles": top_titles,
    }


def _duplicate_event_groups(items: list[dict], section: str) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    for item in items:
        if item.get("section") != section:
            continue
        group = item.get("event_cluster_key") or item.get("event_group_key") or item.get("duplicate_group_id")
        if not group:
            continue
        groups.setdefault(group, []).append(item.get("title"))
    filtered = {group: titles[:3] for group, titles in groups.items() if len(titles) > 1}
    return dict(sorted(filtered.items(), key=lambda entry: len(entry[1]), reverse=True))


def _summary_validation_stats(items: list[dict]) -> dict[str, Any]:
    stats = Counter()
    bad_examples: list[dict[str, str | None]] = []
    for item in items:
        stats[item.get("summary_validation") or "unknown"] += 1
        stats[item.get("summary_source") or "unknown_source"] += 1
        if item.get("summary_validation") == "regenerated":
            stats["summary_regenerated"] += 1
        if item.get("summary_source") == "title_only":
            stats["summary_title_only"] += 1
        if item.get("summary_validation") == "ok":
            stats["summary_ok"] += 1
        if item.get("bad_summary_reason"):
            bad_examples.append(
                {
                    "title": item.get("title"),
                    "bad_summary_reason": item.get("bad_summary_reason"),
                    "summary_source": item.get("summary_source"),
                    "summary_zh": item.get("summary_zh"),
                }
            )
    return {
        "summary_ok": stats.get("summary_ok", 0),
        "summary_regenerated": stats.get("summary_regenerated", 0),
        "summary_title_only": stats.get("summary_title_only", 0),
        "bad_summary_examples": bad_examples[:5],
    }


def _source_quality_summary(items: list[dict]) -> dict[str, int]:
    return dict(Counter(item.get("source_quality", "unknown") for item in items))


def _source_coverage_diagnostics(
    raw_items: list[dict],
    quality_items: list[dict],
    selected_items: list[dict],
    target_date,
) -> dict:
    target = target_date.isoformat()
    quality_urls = {item.get("url") for item in quality_items}
    selected_urls = {item.get("url") for item in selected_items}
    groups_by_section: dict[str, dict[str, dict[str, int]]] = {"domestic": {}, "international": {}}
    for item in raw_items:
        section = item.get("section")
        if section not in groups_by_section:
            continue
        group = item.get("source_group") or item.get("source") or "unknown"
        entry = groups_by_section[section].setdefault(
            group,
            {"raw_count": 0, "target_date_count": 0, "quality_count": 0, "selected_count": 0, "date_missing_count": 0},
        )
        entry["raw_count"] += 1
        if not item.get("published_date"):
            entry["date_missing_count"] += 1
        if item.get("published_date") == target:
            entry["target_date_count"] += 1
        if item.get("url") in quality_urls:
            entry["quality_count"] += 1
        if item.get("url") in selected_urls:
            entry["selected_count"] += 1

    return {
        "domestic": dict(sorted(groups_by_section["domestic"].items(), key=lambda item: item[1]["raw_count"], reverse=True)),
        "international": dict(sorted(groups_by_section["international"].items(), key=lambda item: item[1]["raw_count"], reverse=True)),
        "domestic_shortage_reason": _shortage_reason(groups_by_section["domestic"]),
        "international_shortage_reason": _shortage_reason(groups_by_section["international"]),
    }


def _shortage_reason(groups: dict[str, dict[str, int]]) -> str:
    selected = sum(group["selected_count"] for group in groups.values())
    target = sum(group["target_date_count"] for group in groups.values())
    quality = sum(group["quality_count"] for group in groups.values())
    missing = sum(group["date_missing_count"] for group in groups.values())
    if selected >= 8:
        return "ok"
    if not groups or sum(group["raw_count"] for group in groups.values()) == 0:
        return "source_shortage"
    if target < 8:
        return "source_shortage" if missing < target else "date_parse_problem"
    if quality < 8:
        return "quality_filter_too_strict"
    return "link_validation_failed_or_duplicate_too_many"


def _print_debug_keyword(
    keyword: str,
    raw_items: list[dict],
    quality_items: list[dict],
    selected_items: list[dict],
    excluded_watchlist: list[dict],
) -> None:
    keyword_cf = keyword.casefold()
    quality_urls = {item.get("url") for item in quality_items}
    selected_urls = {item.get("url") for item in selected_items}
    excluded_by_url = {item.get("url"): item for item in excluded_watchlist}
    matches: list[tuple[dict, str, str | None]] = []

    for item in raw_items:
        blob = f"{item.get('title', '')} {item.get('url', '')}".casefold()
        if keyword_cf not in blob:
            continue
        status = "raw"
        exclusion_reason = None
        if item.get("url") in selected_urls:
            status = "selected"
        elif item.get("url") in quality_urls:
            status = "filtered"
        elif item.get("url") in excluded_by_url:
            status = "excluded"
            exclusion_reason = excluded_by_url[item.get("url")].get("exclusion_reason")
        matches.append((item, status, exclusion_reason))

    print(f'Debug keyword: "{keyword}"')
    print(f"Matches: {len(matches)}")
    for item, status, exclusion_reason in matches:
        print(
            f"title={item.get('title')} | source={item.get('source')} | "
            f"raw_pubdate={item.get('original_pubdate')} | parsed_date={item.get('published_date')} | "
            f"source_timezone_date={item.get('source_timezone_date')} | target_timezone_date={item.get('target_timezone_date')} | "
            f"status={status} | exclusion_reason={exclusion_reason} | "
            f"bucket={item.get('category_bucket')} | event_fingerprint={item.get('event_fingerprint')} | "
            f"duplicate_group_id={item.get('duplicate_group_id')} | summary_source={item.get('summary_source')} | "
            f"summary_confidence={item.get('summary_confidence')} | summary_validation={item.get('summary_validation')} | "
            f"bad_summary_reason={item.get('bad_summary_reason')} | url={item.get('url')}"
        )


if __name__ == "__main__":
    sys.exit(main())
