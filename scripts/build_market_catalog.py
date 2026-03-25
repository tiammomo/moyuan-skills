#!/usr/bin/env python3
"""Build a static HTML catalog for the local skills market draft."""

from __future__ import annotations

import argparse
import html
from pathlib import Path

from market_utils import (
    ROOT,
    collect_valid_manifests,
    dump_json,
    enrich_manifest,
    filter_manifests_for_policy,
    load_bundle_definitions,
    load_json,
    load_publisher_profiles,
    repo_relative_path,
    validate_org_policy,
)


DEFAULT_OUTPUT = ROOT / "dist" / "market"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a static HTML catalog for the local skills market.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT, help="Output directory containing market artifacts.")
    parser.add_argument(
        "--org-policy",
        type=Path,
        default=None,
        help="Optional org market policy. When set, build a filtered org-scoped catalog.",
    )
    return parser


def collect_catalog_inputs(org_policy_path: Path | None) -> tuple[list[dict], list[dict], dict | None, list[str]]:
    manifests, manifest_errors = collect_valid_manifests()
    publisher_profiles, publisher_errors = load_publisher_profiles()
    errors = [*manifest_errors, *publisher_errors]
    policy_payload: dict | None = None
    bundles, bundle_errors = load_bundle_definitions({manifest["id"] for manifest in manifests})
    errors.extend(bundle_errors)

    if org_policy_path is not None:
        resolved_policy = org_policy_path if org_policy_path.is_absolute() else (ROOT / org_policy_path)
        if not resolved_policy.is_file():
            errors.append(f"missing org policy file: {resolved_policy}")
        else:
            policy_payload = load_json(resolved_policy)
            _, policy_errors = validate_org_policy(
                resolved_policy.resolve(),
                publisher_profiles,
                {manifest["id"] for manifest in manifests},
            )
            errors.extend(policy_errors)

    if errors:
        return [], [], None, errors

    if policy_payload is not None:
        manifests = filter_manifests_for_policy(manifests, policy_payload, publisher_profiles)

    manifest_ids = {manifest["id"] for manifest in manifests}
    featured_bundle_ids = set(policy_payload.get("featured_bundles", [])) if policy_payload else set()
    filtered_bundles = []
    for bundle in bundles:
        visible_skill_ids = [skill_id for skill_id in bundle["skills"] if skill_id in manifest_ids]
        if not visible_skill_ids:
            continue
        if policy_payload is not None and featured_bundle_ids and bundle["id"] not in featured_bundle_ids:
            continue
        filtered = dict(bundle)
        filtered["skills"] = visible_skill_ids
        filtered_bundles.append(filtered)

    enriched = [enrich_manifest(manifest, publisher_profiles) for manifest in manifests]
    enriched.sort(key=lambda item: (item["channel"], item["title"].lower()))
    filtered_bundles.sort(key=lambda item: (item["id"] not in featured_bundle_ids, item["title"].lower()))
    return enriched, filtered_bundles, policy_payload, []


def install_spec_path(output_dir: Path, manifest: dict) -> Path:
    return output_dir / "install" / f"{manifest['name']}-{manifest['version']}.json"


def provenance_path(output_dir: Path, manifest: dict) -> Path:
    return output_dir / "provenance" / f"{manifest['name']}-{manifest['version']}.json"


def render_badges(items: list[str], class_name: str) -> str:
    return "".join(f'<span class="{class_name}">{html.escape(item)}</span>' for item in items)


def publisher_meta(manifest: dict) -> str:
    profile = manifest["publisher_profile"]
    verified_badge = (
        '<span class="chip chip--verified">Verified Publisher</span>'
        if profile["verified"]
        else '<span class="chip chip--keyword">Community Publisher</span>'
    )
    return (
        f"<p class=\"meta\"><strong>Publisher:</strong> {html.escape(profile['display_name'])} "
        f"({html.escape(profile['trust_level'])})</p><p class=\"chip-row\">{verified_badge}</p>"
    )


def render_skill_card(manifest: dict, output_dir: Path, detail_prefix: str = "skills/") -> str:
    skill_name = manifest["name"]
    detail_href = f"{detail_prefix}{skill_name}.html"
    install_available = install_spec_path(output_dir, manifest).is_file()
    provenance_available = provenance_path(output_dir, manifest).is_file()
    install_label = "Ready to install" if install_available else "Package pending"
    review_status = manifest["quality"]["review_status"]
    lifecycle_status = manifest["lifecycle"]["status"]
    permissions = manifest["permissions"]
    permission_summary = ", ".join(
        [
            f"workspace:{permissions['workspace']}",
            f"shell:{permissions['shell']}",
            f"network:{permissions['network']}",
            f"secrets:{permissions['secrets']}",
        ]
    )
    return f"""
    <article class="skill-card">
      <div class="skill-card__top">
        <p class="channel">{html.escape(manifest['channel'].upper())}</p>
        <p class="install-status">{html.escape(install_label)}</p>
      </div>
      <h3><a href="{detail_href}">{html.escape(manifest['title'])}</a></h3>
      <p class="summary">{html.escape(manifest['summary'])}</p>
      {publisher_meta(manifest)}
      <div class="chip-row">{render_badges(manifest['categories'], 'chip chip--category')}</div>
      <div class="chip-row">{render_badges(manifest['tags'], 'chip chip--tag')}</div>
      <div class="chip-row">{render_badges(manifest['distribution']['capabilities'], 'chip chip--keyword')}</div>
      <p class="meta"><strong>Review:</strong> {html.escape(review_status)} | <strong>Lifecycle:</strong> {html.escape(lifecycle_status)} | <strong>Provenance:</strong> {str(provenance_available).lower()}</p>
      <p class="meta"><strong>Permissions:</strong> {html.escape(permission_summary)}</p>
      <p class="meta"><strong>Entry:</strong> <code>{html.escape(manifest['artifacts']['entrypoint'])}</code></p>
    </article>
    """


def render_channel_page(channel: str, manifests: list[dict], output_dir: Path, policy_payload: dict | None) -> str:
    cards = "\n".join(
        render_skill_card(manifest, output_dir, detail_prefix="../skills/")
        for manifest in manifests
        if manifest["channel"] == channel
    )
    card_block = cards or '<p class="empty">No skills published in this channel yet.</p>'
    scope_label = policy_payload["display_name"] if policy_payload else "Moyuan Skills Market"
    return page_shell(
        title=f"{channel.title()} Channel",
        eyebrow="Skills Market Channel",
        intro=f"{scope_label}: {channel.title()} currently contains {sum(1 for item in manifests if item['channel'] == channel)} skill(s).",
        body=f'<section class="grid">{card_block}</section>',
        nav_links=[
            ('../index.html', 'Catalog home'),
            ('stable.html', 'Stable'),
            ('beta.html', 'Beta'),
            ('internal.html', 'Internal'),
        ],
        relative_prefix="..",
    )


def render_bundle_card(bundle: dict, manifests_by_id: dict[str, dict]) -> str:
    skill_labels = ", ".join(manifests_by_id[skill_id]["title"] for skill_id in bundle["skills"] if skill_id in manifests_by_id)
    return f"""
    <article class="skill-card">
      <div class="skill-card__top">
        <p class="channel">Bundle</p>
        <p class="install-status">{html.escape(bundle['status'])}</p>
      </div>
      <h3>{html.escape(bundle['title'])}</h3>
      <p class="summary">{html.escape(bundle['summary'])}</p>
      <div class="chip-row">{render_badges(bundle['use_cases'], 'chip chip--category')}</div>
      <div class="chip-row">{render_badges(bundle['keywords'], 'chip chip--tag')}</div>
      <p class="meta"><strong>Skills:</strong> {html.escape(skill_labels)}</p>
    </article>
    """


def detail_rows(manifest: dict, output_dir: Path) -> str:
    install_spec = install_spec_path(output_dir, manifest)
    provenance = provenance_path(output_dir, manifest)
    publisher_profile = manifest["publisher_profile"]
    install_command = (
        f"python scripts/skills_market.py install {repo_relative_path(install_spec)} --dry-run"
        if install_spec.is_file()
        else "Package this skill first with: python scripts/skills_market.py package "
        + manifest["name"]
    )
    return f"""
    <section class="detail-panel">
      <h2>Overview</h2>
      <p>{html.escape(manifest['description'])}</p>
      <dl class="detail-list">
        <dt>Skill ID</dt><dd><code>{html.escape(manifest['id'])}</code></dd>
        <dt>Publisher</dt><dd>{html.escape(publisher_profile['display_name'])}</dd>
        <dt>Trust</dt><dd>{html.escape(publisher_profile['trust_level'])} / verified={str(publisher_profile['verified']).lower()}</dd>
        <dt>Version</dt><dd>{html.escape(manifest['version'])}</dd>
        <dt>Channel</dt><dd>{html.escape(manifest['channel'])}</dd>
        <dt>Review</dt><dd>{html.escape(manifest['quality']['review_status'])}</dd>
        <dt>Lifecycle</dt><dd>{html.escape(manifest['lifecycle']['status'])}</dd>
        <dt>Docs</dt><dd><code>{html.escape(manifest['artifacts']['docs'])}</code></dd>
        <dt>Entrypoint</dt><dd><code>{html.escape(manifest['artifacts']['entrypoint'])}</code></dd>
      </dl>
    </section>
    <section class="detail-panel">
      <h2>Permissions</h2>
      <dl class="detail-list">
        <dt>Workspace</dt><dd>{html.escape(manifest['permissions']['workspace'])}</dd>
        <dt>Shell</dt><dd>{html.escape(manifest['permissions']['shell'])}</dd>
        <dt>Network</dt><dd>{html.escape(manifest['permissions']['network'])}</dd>
        <dt>Secrets</dt><dd>{html.escape(manifest['permissions']['secrets'])}</dd>
        <dt>Human review</dt><dd>{str(manifest['permissions']['human_review_required']).lower()}</dd>
      </dl>
    </section>
    <section class="detail-panel">
      <h2>Quality</h2>
      <dl class="detail-list">
        <dt>Checker</dt><dd><code>{html.escape(manifest['quality']['checker'])}</code></dd>
        <dt>Eval</dt><dd><code>{html.escape(manifest['quality']['eval'])}</code></dd>
        <dt>Install spec</dt><dd><code>{html.escape(repo_relative_path(install_spec)) if install_spec.is_file() else 'not generated yet'}</code></dd>
        <dt>Provenance</dt><dd><code>{html.escape(repo_relative_path(provenance)) if provenance.is_file() else 'not generated yet'}</code></dd>
      </dl>
    </section>
    <section class="detail-panel">
      <h2>Discovery</h2>
      <p class="chip-row">{render_badges(manifest['categories'], 'chip chip--category')}</p>
      <p class="chip-row">{render_badges(manifest['tags'], 'chip chip--tag')}</p>
      <p class="chip-row">{render_badges(manifest['search']['keywords'], 'chip chip--keyword')}</p>
      <p class="chip-row">{render_badges(manifest['distribution']['capabilities'], 'chip chip--keyword')}</p>
      <p class="meta"><strong>Related:</strong> {html.escape(', '.join(manifest['search']['related_skills']))}</p>
      <p class="meta"><strong>Bundles:</strong> {html.escape(', '.join(manifest['distribution']['starter_bundle_ids']))}</p>
    </section>
    <section class="detail-panel">
      <h2>Install</h2>
      <pre><code>{html.escape(install_command)}</code></pre>
    </section>
    """


def page_shell(
    *,
    title: str,
    eyebrow: str,
    intro: str,
    body: str,
    nav_links: list[tuple[str, str]],
    relative_prefix: str,
) -> str:
    nav = " ".join(f'<a href="{html.escape(href)}">{html.escape(label)}</a>' for href, label in nav_links)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)} | Moyuan Skills Market</title>
  <style>
    :root {{
      --bg: #f3efe4;
      --paper: #fffdf7;
      --ink: #1e2d24;
      --muted: #5e6e63;
      --line: #d5ccb7;
      --accent: #b5482c;
      --accent-soft: #f0ddcf;
      --olive: #5f7a5f;
      --shadow: 0 18px 50px rgba(48, 35, 19, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Segoe UI", "PingFang SC", sans-serif;
      background: radial-gradient(circle at top, #fdf7eb 0%, var(--bg) 55%, #ece5d6 100%);
      color: var(--ink);
      line-height: 1.6;
    }}
    a {{ color: inherit; }}
    .shell {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 40px 20px 80px;
    }}
    .hero {{
      background: linear-gradient(145deg, rgba(255,253,247,0.98), rgba(248,240,225,0.96));
      border: 1px solid var(--line);
      border-radius: 28px;
      padding: 28px;
      box-shadow: var(--shadow);
    }}
    .eyebrow {{
      letter-spacing: 0.12em;
      text-transform: uppercase;
      font-size: 12px;
      color: var(--olive);
      margin: 0 0 10px;
    }}
    h1 {{
      margin: 0;
      font-size: clamp(2rem, 4vw, 3.5rem);
      line-height: 1.05;
    }}
    .intro {{
      max-width: 820px;
      color: var(--muted);
      font-size: 1.05rem;
      margin: 14px 0 0;
    }}
    nav {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-top: 18px;
    }}
    nav a {{
      text-decoration: none;
      padding: 8px 14px;
      border-radius: 999px;
      border: 1px solid var(--line);
      background: rgba(255,255,255,0.7);
    }}
    .section {{
      margin-top: 28px;
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: 24px;
      padding: 24px;
      box-shadow: var(--shadow);
    }}
    .grid {{
      display: grid;
      gap: 18px;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    }}
    .skill-card, .detail-panel {{
      border: 1px solid var(--line);
      border-radius: 20px;
      padding: 18px;
      background: rgba(255,255,255,0.72);
    }}
    .skill-card__top {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: center;
    }}
    .channel, .install-status {{
      margin: 0;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--olive);
    }}
    .summary, .meta, .empty {{
      color: var(--muted);
    }}
    .chip-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin: 12px 0;
    }}
    .chip {{
      display: inline-flex;
      align-items: center;
      padding: 6px 10px;
      border-radius: 999px;
      font-size: 0.85rem;
      border: 1px solid var(--line);
      background: #fff;
    }}
    .chip--category {{ background: #edf4ea; }}
    .chip--tag {{ background: #fff4e8; }}
    .chip--keyword {{ background: var(--accent-soft); }}
    .chip--verified {{ background: #ddeee0; border-color: #87a88c; }}
    .channel-strip {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 14px;
    }}
    .channel-stat {{
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 16px;
      background: rgba(255,255,255,0.75);
    }}
    .channel-stat strong {{
      display: block;
      font-size: 1.7rem;
      margin-top: 6px;
    }}
    .detail-layout {{
      display: grid;
      gap: 18px;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    }}
    .detail-list {{
      display: grid;
      grid-template-columns: 120px 1fr;
      gap: 8px 12px;
      margin: 0;
    }}
    .detail-list dt {{
      font-weight: 700;
    }}
    pre {{
      margin: 0;
      overflow-x: auto;
      padding: 14px;
      border-radius: 14px;
      background: #1d261f;
      color: #f7f4ea;
    }}
    footer {{
      margin-top: 24px;
      color: var(--muted);
      font-size: 0.95rem;
    }}
  </style>
</head>
<body>
  <main class="shell">
    <section class="hero">
      <p class="eyebrow">{html.escape(eyebrow)}</p>
      <h1>{html.escape(title)}</h1>
      <p class="intro">{html.escape(intro)}</p>
      <nav>{nav}</nav>
    </section>
    <section class="section">
      {body}
    </section>
    <footer>
      Generated by <code>{html.escape(relative_prefix + '/scripts/build_market_catalog.py' if relative_prefix != '.' else 'scripts/build_market_catalog.py')}</code>.
    </footer>
  </main>
</body>
</html>
"""


def build_home_page(manifests: list[dict], bundles: list[dict], output_dir: Path, policy_payload: dict | None) -> str:
    counts = {channel: sum(1 for item in manifests if item["channel"] == channel) for channel in ("stable", "beta", "internal")}
    featured = "\n".join(render_skill_card(manifest, output_dir) for manifest in manifests[:6])
    manifests_by_id = {manifest["id"]: manifest for manifest in manifests}
    bundle_cards = "\n".join(render_bundle_card(bundle, manifests_by_id) for bundle in bundles[:3])
    category_counts: dict[str, int] = {}
    for manifest in manifests:
        for category in manifest["categories"]:
            category_counts[category] = category_counts.get(category, 0) + 1
    categories = "".join(
        f'<span class="chip chip--category">{html.escape(category)} ({count})</span>'
        for category, count in sorted(category_counts.items())
    )
    if policy_payload is None:
        title = "Moyuan Skills Market"
        eyebrow = "Static Catalog"
        intro = "A generated static market view over the current skills manifests, install specs, review signals, and channel structure."
    else:
        title = policy_payload["display_name"]
        eyebrow = "Org Market Catalog"
        intro = (
            f"A policy-filtered catalog generated from {policy_payload['org_id']}. "
            "Only verified and allowlisted skills that match the org rules are shown here."
        )
    body = f"""
    <section class="channel-strip">
      <article class="channel-stat"><p>Stable</p><strong>{counts['stable']}</strong><a href="channels/stable.html">Open channel</a></article>
      <article class="channel-stat"><p>Beta</p><strong>{counts['beta']}</strong><a href="channels/beta.html">Open channel</a></article>
      <article class="channel-stat"><p>Internal</p><strong>{counts['internal']}</strong><a href="channels/internal.html">Open channel</a></article>
    </section>
    <h2>Featured skills</h2>
    <section class="grid">{featured}</section>
    <h2>Starter bundles</h2>
    <section class="grid">{bundle_cards or '<p class="empty">No starter bundles generated yet.</p>'}</section>
    <h2>Category map</h2>
    <p class="chip-row">{categories}</p>
    """
    return page_shell(
        title=title,
        eyebrow=eyebrow,
        intro=intro,
        body=body,
        nav_links=[
            ("index.html", "Catalog home"),
            ("channels/stable.html", "Stable"),
            ("channels/beta.html", "Beta"),
            ("channels/internal.html", "Internal"),
        ],
        relative_prefix=".",
    )


def build_catalog_json(manifests: list[dict], bundles: list[dict], output_dir: Path, policy_payload: dict | None) -> dict:
    payload = {
        "generated_from": "scripts/build_market_catalog.py",
        "org_policy": policy_payload["org_id"] if policy_payload else None,
        "skills": [],
        "bundles": bundles,
    }
    for manifest in manifests:
        payload["skills"].append(
            {
                "id": manifest["id"],
                "name": manifest["name"],
                "title": manifest["title"],
                "version": manifest["version"],
                "publisher": manifest["publisher"],
                "publisher_display_name": manifest["publisher_profile"]["display_name"],
                "publisher_verified": manifest["publisher_profile"]["verified"],
                "trust_level": manifest["publisher_profile"]["trust_level"],
                "channel": manifest["channel"],
                "summary": manifest["summary"],
                "categories": manifest["categories"],
                "tags": manifest["tags"],
                "capabilities": manifest["distribution"]["capabilities"],
                "starter_bundle_ids": manifest["distribution"]["starter_bundle_ids"],
                "keywords": manifest["search"]["keywords"],
                "related_skills": manifest["search"]["related_skills"],
                "review_status": manifest["quality"]["review_status"],
                "lifecycle_status": manifest["lifecycle"]["status"],
                "provenance_path": repo_relative_path(provenance_path(output_dir, manifest)),
                "install_spec": repo_relative_path(install_spec_path(output_dir, manifest)),
                "install_available": install_spec_path(output_dir, manifest).is_file(),
                "docs": manifest["artifacts"]["docs"],
            }
        )
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    output_dir = (args.output_dir if args.output_dir.is_absolute() else (ROOT / args.output_dir)).resolve()
    manifests, bundles, policy_payload, errors = collect_catalog_inputs(args.org_policy)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    if policy_payload is None:
        site_dir = output_dir / "site"
    else:
        site_dir = output_dir / "orgs" / policy_payload["org_id"] / "site"

    channels_dir = site_dir / "channels"
    skills_dir = site_dir / "skills"
    site_dir.mkdir(parents=True, exist_ok=True)
    channels_dir.mkdir(parents=True, exist_ok=True)
    skills_dir.mkdir(parents=True, exist_ok=True)

    (site_dir / "index.html").write_text(build_home_page(manifests, bundles, output_dir, policy_payload), encoding="utf-8")

    for channel in ("stable", "beta", "internal"):
        (channels_dir / f"{channel}.html").write_text(
            render_channel_page(channel, manifests, output_dir, policy_payload),
            encoding="utf-8",
        )

    for manifest in manifests:
        detail_html = page_shell(
            title=manifest["title"],
            eyebrow="Skill Detail",
            intro=manifest["summary"],
            body=f'<section class="detail-layout">{detail_rows(manifest, output_dir)}</section>',
            nav_links=[
                ("../index.html", "Catalog home"),
                (f"../channels/{manifest['channel']}.html", f"{manifest['channel'].title()} channel"),
                (f"{manifest['name']}.html", manifest["title"]),
            ],
            relative_prefix="..",
        )
        (skills_dir / f"{manifest['name']}.html").write_text(detail_html, encoding="utf-8")

    dump_json(site_dir / "catalog.json", build_catalog_json(manifests, bundles, output_dir, policy_payload))
    print(f"Built static market catalog in {site_dir}")
    if policy_payload is not None:
        print(f"Catalog policy: {policy_payload['org_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
