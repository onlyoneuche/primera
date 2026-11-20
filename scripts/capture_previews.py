"""Capture the real app in installed Chrome; never substitute model responses."""
import argparse
import asyncio
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit
from playwright.async_api import async_playwright
from ml.config import ROOT

VIEWPORTS = {'phone': {'width':390,'height':844}, 'desktop':{'width':1280,'height':800}}


async def capture(base_url, channel):
    origin = urlsplit(base_url)
    destination = ROOT/'docs/design/previews'
    destination.mkdir(parents=True,exist_ok=True)
    copy = json.loads((ROOT/'config/copy.json').read_text())
    requests, errors, screenshots = [], [], []
    async with async_playwright() as playwright:
        # A fresh temporary browser profile keeps the owner's existing tabs/data untouched.
        browser = await playwright.chromium.launch(channel=channel, headless=True)
        context = await browser.new_context(viewport=VIEWPORTS['phone'], reduced_motion='reduce')
        page = await context.new_page()
        page.on('request',lambda request:requests.append(request.url))
        page.on('pageerror',lambda error:errors.append(str(error)))
        mode = 'normal'
        release = asyncio.Event()

        async def route_prediction(route):
            if mode == 'abort':
                await route.abort('failed')
            else:
                if mode == 'hold':
                    await release.wait()
                await route.continue_()
        await page.route('**/predict',route_prediction)

        async def privacy():
            assert await page.evaluate('localStorage.length') == 0
            assert await page.evaluate('sessionStorage.length') == 0
            assert await page.evaluate('document.cookie') == ''
            assert await page.evaluate('indexedDB.databases()') == []
            assert await context.cookies() == []
            assert not errors, 'Browser JavaScript error; do not publish previews.'
            assert all((urlsplit(url).scheme,urlsplit(url).netloc) == (origin.scheme,origin.netloc)
                       for url in requests), 'A runtime request left the app origin.'

        async def shoot(name):
            for device,dimensions in VIEWPORTS.items():
                await page.set_viewport_size(dimensions)
                await page.evaluate('document.fonts.ready')
                await page.evaluate('scrollTo(0,0)')
                await page.evaluate('() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))')
                assert await page.evaluate('document.documentElement.scrollWidth <= innerWidth'), name
                undersized=await page.evaluate('''() => [...document.querySelectorAll('button,a,input,select')]
                    .filter(el => el.getClientRects().length && !el.closest('[hidden]'))
                    .map(el => el.matches('input[type=radio]') ? el.closest('label') : el)
                    .map(el => el.getBoundingClientRect())
                    .filter(rect => rect.width < 48 || rect.height < 48)
                    .map(rect => ({width:rect.width,height:rect.height}))''')
                assert not undersized, f'Touch target below 48px in {name}: {undersized}'
                await privacy()
                path=destination/f'{name}-{device}.png'
                await page.screenshot(path=str(path),full_page=True,animations='disabled')
                screenshots.append(path.name)

        async def next_question(expected):
            await page.get_by_role('button',name=copy['controls']['next'],exact=True).click()
            await page.get_by_role('heading',name=expected,exact=True).wait_for()

        async def choice(label,next_prompt):
            # Click the full visible label tile, as a pointer user does; the native radio is visually hidden.
            await page.get_by_text(label,exact=True).click()
            assert await page.get_by_role('radio',name=label,exact=True).is_checked()
            await next_question(next_prompt)

        async def finish_choices(married):
            await choice('Married' if married else 'Single',copy['questions'][6]['prompt'])
            await choice('Yes',copy['questions'][7]['prompt'])
            await choice('Yes' if married else 'No',copy['questions'][8]['prompt'])
            await page.get_by_text('Yes' if married else 'No',exact=True).click()

        await page.goto(base_url,wait_until='networkidle')
        await page.get_by_role('heading',name=copy['welcome']['title'],exact=True).wait_for()
        # Complete one phone-sized flow using native keyboard input only, including hidden radios.
        await page.keyboard.press('Tab')
        await page.keyboard.press('Enter')
        async def keys_for_question(index, keys):
            await page.get_by_role('heading',name=copy['questions'][index]['prompt'],exact=True).wait_for()
            for key in keys:
                await page.keyboard.press(key)
        await keys_for_question(0,['Tab','Space','Enter'])
        await keys_for_question(1,['Tab'])
        await page.keyboard.type('21')
        await page.keyboard.press('Enter')
        await keys_for_question(2,['Tab','h','Tab','Tab','Enter'])
        await keys_for_question(3,['Tab','ArrowDown','Enter'])
        await keys_for_question(4,['Tab','Tab','ArrowDown','ArrowDown','ArrowDown','Enter'])
        await keys_for_question(5,['Tab','Space','Enter'])
        await keys_for_question(6,['Tab','Space','Enter'])
        await keys_for_question(7,['Tab','ArrowDown','Enter'])
        await keys_for_question(8,['Tab','ArrowDown','Enter'])
        await page.get_by_role('heading',name=copy['results']['lower']['title'],exact=True).wait_for()
        assert await page.evaluate('document.activeElement.id')=='screen-title'
        for _ in range(4):
            await page.keyboard.press('Tab')
        await page.keyboard.press('Enter')
        await page.get_by_role('heading',name=copy['welcome']['title'],exact=True).wait_for()
        await privacy()
        await shoot('welcome')
        await page.get_by_role('button',name=copy['footer']['about'],exact=True).click()
        await page.get_by_role('dialog').wait_for()
        await shoot('how-this-works')
        await page.keyboard.press('Escape')
        assert await page.get_by_role('button',name=copy['footer']['about'],exact=True).evaluate('(el)=>el===document.activeElement')
        await page.get_by_role('button',name=copy['welcome']['start'],exact=True).click()
        await page.get_by_text('Female',exact=True).click()
        await shoot('choice-question')
        await choice('Female',copy['questions'][1]['prompt'])
        await page.get_by_role('button',name=copy['controls']['back'],exact=True).click()
        assert await page.get_by_role('radio',name='Female',exact=True).is_checked()
        await next_question(copy['questions'][1]['prompt'])
        await shoot('age-question')
        await page.get_by_role('spinbutton').fill('15')
        await page.get_by_role('button',name=copy['controls']['next'],exact=True).click()
        await page.get_by_role('alert').filter(has_text=copy['questions'][1]['error']).wait_for()
        await shoot('error-state')
        await page.get_by_role('spinbutton').fill('21')
        await next_question(copy['questions'][2]['prompt'])
        await shoot('faculty-question')
        await page.get_by_role('combobox').select_option('Health sciences')
        await next_question(copy['questions'][3]['prompt'])
        await choice('Year 2',copy['questions'][4]['prompt'])
        await page.get_by_role('radio',name=copy['controls']['scale5'],exact=True).check()
        await shoot('cgpa-question')
        await choice('3.75 to 4.37',copy['questions'][5]['prompt'])
        await finish_choices(False)
        mode='hold'
        async with page.expect_response(lambda response:urlsplit(response.url).path=='/predict') as pending:
            await page.get_by_role('button',name=copy['controls']['next'],exact=True).click()
            await page.get_by_role('heading',name=copy['loading'],exact=True).wait_for()
            # Hold a genuine request only long enough to photograph the actual loading UI.
            await shoot('loading')
            release.set()
            response=await pending.value
        assert response.headers.get('cache-control') == 'no-store'
        body=await response.json()
        assert body['category'] == 'lower', 'Expected test fixture no longer yields lower; review actual model.'
        assert set(body)=={'category','label','title','message','disclaimer','out_of_range_notes','model_note'}
        await page.get_by_role('heading',name=body['title'],exact=True).wait_for()
        assert await page.evaluate('document.activeElement.id') == 'screen-title'
        await shoot('lower-result')
        await page.get_by_role('button',name=copy['controls']['restart'],exact=True).click()
        await page.get_by_role('button',name=copy['welcome']['start'],exact=True).click()
        assert await page.locator('input:checked').count() == 0
        await choice('Male',copy['questions'][1]['prompt'])
        assert await page.get_by_role('spinbutton').input_value() == ''
        await page.get_by_role('spinbutton').fill('26')
        await next_question(copy['questions'][2]['prompt'])
        await page.get_by_role('combobox').select_option('Law')
        await next_question(copy['questions'][3]['prompt'])
        await choice('Year 4 or above',copy['questions'][4]['prompt'])
        assert await page.get_by_role('radio',name=copy['controls']['scale4'],exact=True).is_checked()
        await choice('3.50 to 4.00',copy['questions'][5]['prompt'])
        await finish_choices(True)
        mode='abort'
        await page.get_by_role('button',name=copy['controls']['next'],exact=True).click()
        await page.get_by_role('heading',name=copy['errors']['network_title'],exact=True).wait_for()
        await shoot('network-error')
        mode='normal'
        async with page.expect_response(lambda response:urlsplit(response.url).path=='/predict') as pending:
            await page.get_by_role('button',name=copy['controls']['retry'],exact=True).click()
            response=await pending.value
        body=await response.json()
        assert body['category']=='higher'
        assert len(body['out_of_range_notes'])==2
        await page.get_by_role('heading',name=body['title'],exact=True).wait_for()
        assert await page.evaluate('document.activeElement.id')=='screen-title'
        await shoot('higher-result')
        await privacy()
        assert len(screenshots)==22
        report={'browser':await browser.version() if callable(browser.version) else browser.version,
                'browser_channel':channel,'viewports':VIEWPORTS,'screenshots':screenshots,
                'privacy':{'local_storage_keys':0,'session_storage_keys':0,'indexed_databases':0,
                           'cookies':0,'third_party_requests':0,'javascript_errors':len(errors)},
                'real_model_categories_checked':['lower','higher'],
                'checks':['keyboard_only_phone_flow','back_preserves_selection','validation','cgpa_mapping','restart_clearing','result_focus','dialog_focus_restoration',
                          'retry','age_and_year_notes','prediction_no_store','no_horizontal_overflow','48px_touch_targets'],
                'asset_sha256':{str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in sorted((ROOT/'app/static').rglob('*')) if path.is_file()}}
        (destination/'browser_checks.json').write_text(json.dumps(report,indent=2)+'\n')
        await browser.close()
        print('Captured 22 real-app screenshots; real model categories, retry, focus, storage, cookies, and same-origin checks passed.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url',default='http://127.0.0.1:8000')
    parser.add_argument('--channel',default='chrome',help='Installed browser channel; default chrome (no extra browser download).')
    args=parser.parse_args()
    if urlsplit(args.url).hostname not in {'127.0.0.1','localhost','::1'}:
        parser.error('Preview checks are limited to a local application.')
    asyncio.run(capture(args.url,args.channel))


if __name__=='__main__':
    main()
