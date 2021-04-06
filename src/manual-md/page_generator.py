# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% [markdown]
# ## Import modules and define global constants

# %%
# this py file is generated from notebook (ipynb file)

import shutil
from pathlib import Path
from datetime import date, timedelta
from opencc import OpenCC

digest_start = date(2020, 3, 1)
start_year = 2020
cur_year = 2021
lastest_month = 4
lastest_day = 1
one_day = timedelta(days=1)

 # not using strftime("%B") for months since it depends on the current locale
month_en = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')
weekday_zh_hant = ('週一', '週二', '週三', '週四', '週五', '週六', '週日')
weekday_zh_hans = ('周一', '周二', '周三', '周四', '周五', '周六', '周日')
weekday_en = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')

# %% [markdown]
# ## Get manual md path and content

# %%
def path_manual(y, m, d, locale='zh-Hant'):
    '''
    Return path like `./manual[_{locale}]/2020/3/18.md`
    '''
    dir_name = 'manual' if locale == 'zh-Hant' else f'manual_{locale}'
    return Path(dir_name, str(y), str(m), f'{d}.md')

def manual_content(y, m, d, locale='zh-Hant'):
    md_file = path_manual(y, m, d)
    md_file_sc = path_manual(y, m, d, 'zh-Hans')

    if locale == 'zh-Hant':
        if Path(md_file).is_file():
            with open(md_file, 'r') as f:
                content = f.read()
            return content
        return ''

    if locale == 'zh-Hans':
        if Path(md_file_sc).is_file():
            with open(md_file_sc, 'r') as f:
                content = f.read()
            return content
        else:
            t2s = OpenCC('tw2sp.json')
            return t2s.convert(manual_content(y, m, d))

    # for any other locales
    return ''

# manual_content(2021,3,1,'zh-Hans')

# %% [markdown]
# ## Generate digest content string
# 
# For mdx that will be generated

# %%
def digest_content(y, m, d, locale='zh-Hant'):
    '''Return the string for the page of y/m/d'''
    dt = date(y, m, d)
    man = manual_content(y, m, d, locale)

    front_matter = f'''---
title: {m} 月 {d} 日（{weekday_zh_hant[dt.weekday()]}）
description: {y} 年 {m} 月 {d} 日法國新冠肺炎疫情匯報。法國 COVID-19 日誌第 {(dt - digest_start).days + 1} 篇。
---
'''
    export_import = f'''
export const date = "{dt.strftime('%Y-%m-%d')}";
import {{ Subtitle, Grace, Fish, OfficialData, SourceFb, Figure, ChartCases }} from "@site/src/scripts/digest-components";
'''
    subtitle = '''
<Subtitle date={date} />
'''
    main_img = '''
<Figure date={date}></Figure>
'''
    sourceOfData = '''
<div className="comment--translc_gray">📈 數據來源：請參考附錄<a href="../../sources">資料來源</a>。</div>
'''
    chartCases = '''
<ChartCases date={date} />
'''
    official_data_heading = '''
## 法國官方數據 {#official-data}
'''
    official_data = '''
<OfficialData date={date} />
'''
    news_only_zh = ''
    sourceFb = '''
<SourceFb date={date} />
'''
    news_heading = '''
## 本日新聞重點 {#news}
'''

    # overwrite some strings for `zh-Hans`
    if locale == 'zh-Hans':
        front_matter = f'''---
title: {m} 月 {d} 日（{weekday_zh_hans[dt.weekday()]}）
description: {y} 年 {m} 月 {d} 日法国新冠肺炎疫情汇报。法国 COVID-19 日志第 {(dt - digest_start).days + 1} 篇。
---
'''
        sourceOfData = '''
<div className="comment--translc_gray">📈 数据来源：请参考附录<a href="../../sources">资料来源</a>。</div>
'''
        official_data_heading = '''
## 法国官方数据 {#official-data}
'''
        news_heading = '''
## 本日新闻重点 {#news}
'''

    # overwrite some strings for `en`
    if locale == 'en':        
        front_matter = f'''---
title: {weekday_en[dt.weekday()]}, {d} {month_en[m-1]}
sidebar_label: {weekday_en[dt.weekday()][:3]}. {d} {month_en[m-1]}
description: Daily digest of COVID-19 in France on {d} {month_en[m-1]} {y}. Day {(dt - digest_start).days + 1}.
---
'''
        sourceOfData = '''
<div className="comment--translc_gray">📈 Data sources: see <a href="../../sources">Appendices - Sources</a>.</div>
'''
        # add `dateFmt="d/m"`
        chartCases = '''
<ChartCases date={date} dateFmt="d/m" />
'''
        official_data_heading = '''
## Official Data {#official-data}
'''
        news_only_zh = '''
<div className="comment--translc_gray">📢 For the COVID-19 Daily News Digest, it is only available in <strong>traditional Chinese</strong> and <strong>simplified Chinese</strong> at the moment.</div>
'''
        news_heading = '''
## COVID-19 Daily News Digest {#news}
'''

    if man:
        man = '\n' + man
    else:
        sourceFb = ''
        news_heading = ''

    # There's no data for 2020/3/1
    if dt == date(2020,3,1):
        return  front_matter + export_import + subtitle + main_img + man

    return front_matter + export_import + subtitle + main_img + sourceOfData + chartCases + official_data_heading + official_data + news_only_zh + sourceFb + news_heading + man

# print(digest_content(2021,3,2, 'en'))

# %% [markdown]
# ## Generate digest pages
# 
# Generate
# - `/docs/{year}/{month_en_lower}/{day}.mdx`
# - `/i18n/{locale}/docusaurus-plugin-content-docs/current/{year}/{month_en_lower}/{day}.mdx`
# with content given by `digest_content` function
# 
# Note: Should generate pages ONLY for dates after 2020/3/1 (included)

# %%
def generate_a_page(y, m, d):
    '''
    Generate the digest page of date d/m/y for zh-Hant, zh-Hans and en
    '''
    folder = Path('..', '..', 'docs', str(y), month_en[m-1].lower())
    folder_sc = Path('..', '..', 'i18n', 'zh-Hans', 'docusaurus-plugin-content-docs', 'current', str(y), month_en[m-1].lower())
    folder_en = Path('..', '..', 'i18n', 'en', 'docusaurus-plugin-content-docs', 'current', str(y), month_en[m-1].lower())
    mdx = Path(folder, f'{d}.mdx')
    mdx_sc = Path(folder_sc, f'{d}.mdx')
    mdx_en = Path(folder_en, f'{d}.mdx')

    # write file: zh-Hant
    folder.mkdir(parents=True, exist_ok=True)
    with open(mdx, 'w') as f:
        f.write(digest_content(y, m, d))
    
    # write file: zh-Hans
    folder_sc.mkdir(parents=True, exist_ok=True)
    with open(mdx_sc, 'w') as f:
        f.write(digest_content(y, m, d, 'zh-Hans'))

    # write file: en
    folder_en.mkdir(parents=True, exist_ok=True)
    with open(mdx_en, 'w') as f:
        f.write(digest_content(y, m, d, 'en'))

    print(f'> generated mdx for {y}/{m}/{d} in `/docs/` and `/i18n/{{locale}}/docusaurus-plugin-content-docs/current/`')

def generate_pages(s_y, s_m, s_d, e_y, e_m, e_d):
    s_dt = date(s_y, s_m, s_d)
    e_dt = date(e_y, e_m, e_d)
    n_pages = (e_dt - s_dt).days + 1
    if n_pages < 2:
        raise Exception("The ending date should be at least one day after the starting day.")

    prompt = f'writing {n_pages} pages: from {s_y}/{s_m}/{s_d} to {e_y}/{e_m}/{e_d} in zh-Hant, zh-Hans and en'
    print(f'Start {prompt}...')

    dt = s_dt
    while (dt != e_dt + one_day):
        generate_a_page(dt.year, dt.month, dt.day)
        dt += one_day

    print(f'Finish {prompt}.')

# generate_pages(2020,3,9,2020,3,10)

# %% [markdown]
# ## Create `intro.md` by copying manual `intro.md`
# 
# Copy `./manual/{cur_year}/intro.md` to `/docs/{cur_year}/intro.md`
# 
# Copy `./manual_{locale}/{cur_year}/intro.md` to `/i18n/{locale}/docusaurus-plugin-content-docs/current/{cur_year}/intro.md`

# %%
def create_intro_md(locale='zh-Hant'):
    '''
    Copy `./manual/{cur_year}/intro.md` to `/docs/{cur_year}/intro.md`,
    or `./manual_{locale}/{cur_year}/intro.md` to `/i18n/{locale}/docusaurus-plugin-content-docs/current/{cur_year}/intro.md`.
    '''
    intro_root_dir_from = 'manual' if locale == 'zh-Hant' else f'manual_{locale}'
    intro_md_from = Path(intro_root_dir_from, str(cur_year), 'intro.md')
    intro_dir_to = Path('..', '..', 'docs', str(cur_year)) if locale == 'zh-Hant' else Path('..', '..', 'i18n', locale, 'docusaurus-plugin-content-docs', 'current', str(cur_year))
    intro_md_to = Path(intro_dir_to, 'intro.md')

    # if intro md file doesn't exist, raise an error
    if not intro_md_from.is_file():
        if locale == 'zh-Hant':
            raise Exception(f"File `./manual/{cur_year}/intro.md` doesn't exist, can't copy it to `/docs/{cur_year}/intro.md`.")
        else:
            raise Exception(f"File `./manual_{locale}/{cur_year}/intro.md` doesn't exist, can't copy it to `/i18n/{locale}/docusaurus-plugin-content-docs/current/{cur_year}/intro.md`.")

    # intro md file exists as expected, so copy it
    else:
        intro_dir_to.mkdir(parents=True, exist_ok=True)
        shutil.copy(intro_md_from, intro_md_to)

        # prompt: copy finished
        if locale == 'zh-Hant':
            print(f'Copied `./manual/{cur_year}/intro.md` to `/docs/{cur_year}/intro.md`.')
        else:
            print(f'Copied `./manual_{locale}/{cur_year}/intro.md` to `/i18n/{locale}/docusaurus-plugin-content-docs/current/{cur_year}/intro.md`.')

# create_intro_md('zh-Hant')

# %% [markdown]
# ## Clear generated pages
# 
# Delete folders `/docs/{year}/`, `/i18n/{locale}/docusaurus-plugin-content-docs/current/{year}/` and all their contents

# %%
def clear_generated_pages():
    '''
    Delete folders `/docs/{year}/`, `/i18n/{locale}/docusaurus-plugin-content-docs/current/{year}/` and all their contents
    '''
    print('Start clearing generated files...')

    for y in range(start_year, cur_year + 2):
        dir_to_delete = Path('..', '..', 'docs', str(y))
        dir_to_delete_sc = Path('..', '..', 'i18n', 'zh-Hans', 'docusaurus-plugin-content-docs', 'current', str(y))
        dir_to_delete_en = Path('..', '..', 'i18n', 'en', 'docusaurus-plugin-content-docs', 'current', str(y))

        if dir_to_delete.is_dir():
            shutil.rmtree(dir_to_delete)
            print(f"> deleted folder `{y}` in `/docs/` (as well as all its contents)")

        if dir_to_delete_sc.is_dir():
            shutil.rmtree(dir_to_delete_sc)
            print(f"> deleted folder `{y}` in `/i18n/zh-Hans/docusaurus-plugin-content-docs/current/` (as well as all its contents)")

        if dir_to_delete_en.is_dir():
            shutil.rmtree(dir_to_delete_en)
            print(f"> deleted folder `{y}` in `/i18n/en/docusaurus-plugin-content-docs/current/` (as well as all its contents)")

    print('Finish clearing generated files.')

# clear_generated_pages()

# %% [markdown]
# ## Define and execute the `main` function

# %%
def main():
    clear_generated_pages()

    generate_pages(2020,3,1,cur_year,lastest_month,lastest_day)

    create_intro_md('zh-Hant')
    create_intro_md('zh-Hans')
    create_intro_md('en')

main()

