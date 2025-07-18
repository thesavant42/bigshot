```
2025-07-18T22:55:51.3622646Z Current runner version: '2.326.0'
2025-07-18T22:55:51.3646937Z ##[group]Runner Image Provisioner
2025-07-18T22:55:51.3647980Z Hosted Compute Agent
2025-07-18T22:55:51.3648612Z Version: 20250711.363
2025-07-18T22:55:51.3649178Z Commit: 6785254374ce925a23743850c1cb91912ce5c14c
2025-07-18T22:55:51.3650000Z Build Date: 2025-07-11T20:04:25Z
2025-07-18T22:55:51.3650608Z ##[endgroup]
2025-07-18T22:55:51.3651130Z ##[group]Operating System
2025-07-18T22:55:51.3651796Z Ubuntu
2025-07-18T22:55:51.3652270Z 24.04.2
2025-07-18T22:55:51.3652735Z LTS
2025-07-18T22:55:51.3653244Z ##[endgroup]
2025-07-18T22:55:51.3653756Z ##[group]Runner Image
2025-07-18T22:55:51.3654320Z Image: ubuntu-24.04
2025-07-18T22:55:51.3654899Z Version: 20250710.1.0
2025-07-18T22:55:51.3655944Z Included Software: https://github.com/actions/runner-images/blob/ubuntu24/20250710.1/images/ubuntu/Ubuntu2404-Readme.md
2025-07-18T22:55:51.3657674Z Image Release: https://github.com/actions/runner-images/releases/tag/ubuntu24%2F20250710.1
2025-07-18T22:55:51.3658682Z ##[endgroup]
2025-07-18T22:55:51.3659888Z ##[group]GITHUB_TOKEN Permissions
2025-07-18T22:55:51.3661970Z Contents: read
2025-07-18T22:55:51.3662547Z Metadata: read
2025-07-18T22:55:51.3663138Z SecurityEvents: write
2025-07-18T22:55:51.3663711Z ##[endgroup]
2025-07-18T22:55:51.3665816Z Secret source: Actions
2025-07-18T22:55:51.3666628Z Prepare workflow directory
2025-07-18T22:55:51.4023861Z Prepare all required actions
2025-07-18T22:55:51.4081012Z Getting action download info
2025-07-18T22:55:51.7742840Z ##[group]Download immutable action package 'actions/checkout@v4'
2025-07-18T22:55:51.7744091Z Version: 4.2.2
2025-07-18T22:55:51.7745119Z Digest: sha256:ccb2698953eaebd21c7bf6268a94f9c26518a7e38e27e0b83c1fe1ad049819b1
2025-07-18T22:55:51.7746309Z Source commit SHA: 11bd71901bbe5b1630ceea73d27597364c9af683
2025-07-18T22:55:51.7747080Z ##[endgroup]
2025-07-18T22:55:51.8765395Z ##[group]Download immutable action package 'actions/setup-node@v4'
2025-07-18T22:55:51.8766195Z Version: 4.4.0
2025-07-18T22:55:51.8767078Z Digest: sha256:9427cefe82346e992fb5b949e3569b39d537ae41aa3086483b14eceebfc16bc1
2025-07-18T22:55:51.8768413Z Source commit SHA: 49933ea5288caeca8642d1e84afbd3f7d6820020
2025-07-18T22:55:51.8769086Z ##[endgroup]
2025-07-18T22:55:52.0611455Z Complete job name: frontend-tests
2025-07-18T22:55:52.1271525Z ##[group]Run actions/checkout@v4
2025-07-18T22:55:52.1272378Z with:
2025-07-18T22:55:52.1272777Z   repository: thesavant42/bigshot
2025-07-18T22:55:52.1273446Z   token: ***
2025-07-18T22:55:52.1273836Z   ssh-strict: true
2025-07-18T22:55:52.1274230Z   ssh-user: git
2025-07-18T22:55:52.1274641Z   persist-credentials: true
2025-07-18T22:55:52.1275100Z   clean: true
2025-07-18T22:55:52.1275512Z   sparse-checkout-cone-mode: true
2025-07-18T22:55:52.1276005Z   fetch-depth: 1
2025-07-18T22:55:52.1276417Z   fetch-tags: false
2025-07-18T22:55:52.1276821Z   show-progress: true
2025-07-18T22:55:52.1277237Z   lfs: false
2025-07-18T22:55:52.1277767Z   submodules: false
2025-07-18T22:55:52.1278184Z   set-safe-directory: true
2025-07-18T22:55:52.1278890Z ##[endgroup]
2025-07-18T22:55:52.2423767Z Syncing repository: thesavant42/bigshot
2025-07-18T22:55:52.2426147Z ##[group]Getting Git version info
2025-07-18T22:55:52.2427396Z Working directory is '/home/runner/work/bigshot/bigshot'
2025-07-18T22:55:52.2429288Z [command]/usr/bin/git version
2025-07-18T22:55:52.2476107Z git version 2.50.1
2025-07-18T22:55:52.2508563Z ##[endgroup]
2025-07-18T22:55:52.2521608Z Temporarily overriding HOME='/home/runner/work/_temp/ecefdbbe-d8d7-4ca8-a542-d067532513e1' before making global git config changes
2025-07-18T22:55:52.2524012Z Adding repository directory to the temporary git global config as a safe directory
2025-07-18T22:55:52.2527802Z [command]/usr/bin/git config --global --add safe.directory /home/runner/work/bigshot/bigshot
2025-07-18T22:55:52.2564998Z Deleting the contents of '/home/runner/work/bigshot/bigshot'
2025-07-18T22:55:52.2568983Z ##[group]Initializing the repository
2025-07-18T22:55:52.2573844Z [command]/usr/bin/git init /home/runner/work/bigshot/bigshot
2025-07-18T22:55:52.2637360Z hint: Using 'master' as the name for the initial branch. This default branch name
2025-07-18T22:55:52.2640772Z hint: is subject to change. To configure the initial branch name to use in all
2025-07-18T22:55:52.2642484Z hint: of your new repositories, which will suppress this warning, call:
2025-07-18T22:55:52.2643774Z hint:
2025-07-18T22:55:52.2644676Z hint: 	git config --global init.defaultBranch <name>
2025-07-18T22:55:52.2645753Z hint:
2025-07-18T22:55:52.2646961Z hint: Names commonly chosen instead of 'master' are 'main', 'trunk' and
2025-07-18T22:55:52.2648941Z hint: 'development'. The just-created branch can be renamed via this command:
2025-07-18T22:55:52.2650189Z hint:
2025-07-18T22:55:52.2650867Z hint: 	git branch -m <name>
2025-07-18T22:55:52.2651716Z hint:
2025-07-18T22:55:52.2652809Z hint: Disable this message with "git config set advice.defaultBranchName false"
2025-07-18T22:55:52.2654585Z Initialized empty Git repository in /home/runner/work/bigshot/bigshot/.git/
2025-07-18T22:55:52.2659119Z [command]/usr/bin/git remote add origin https://github.com/thesavant42/bigshot
2025-07-18T22:55:52.2690906Z ##[endgroup]
2025-07-18T22:55:52.2694073Z ##[group]Disabling automatic garbage collection
2025-07-18T22:55:52.2696540Z [command]/usr/bin/git config --local gc.auto 0
2025-07-18T22:55:52.2728904Z ##[endgroup]
2025-07-18T22:55:52.2730974Z ##[group]Setting up auth
2025-07-18T22:55:52.2734947Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
2025-07-18T22:55:52.2768593Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
2025-07-18T22:55:52.3037150Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2025-07-18T22:55:52.3069948Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
2025-07-18T22:55:52.3304530Z [command]/usr/bin/git config --local http.https://github.com/.extraheader AUTHORIZATION: basic ***
2025-07-18T22:55:52.3482710Z ##[endgroup]
2025-07-18T22:55:52.3484327Z ##[group]Fetching the repository
2025-07-18T22:55:52.3487034Z [command]/usr/bin/git -c protocol.version=2 fetch --no-tags --prune --no-recurse-submodules --depth=1 origin +76044d01c59a523512dfd31e795709b6ed3fbcb9:refs/remotes/pull/109/merge
2025-07-18T22:55:53.1283743Z From https://github.com/thesavant42/bigshot
2025-07-18T22:55:53.1285536Z  * [new ref]         76044d01c59a523512dfd31e795709b6ed3fbcb9 -> pull/109/merge
2025-07-18T22:55:53.1291658Z ##[endgroup]
2025-07-18T22:55:53.1293437Z ##[group]Determining the checkout info
2025-07-18T22:55:53.1295364Z ##[endgroup]
2025-07-18T22:55:53.1296644Z [command]/usr/bin/git sparse-checkout disable
2025-07-18T22:55:53.1300448Z [command]/usr/bin/git config --local --unset-all extensions.worktreeConfig
2025-07-18T22:55:53.1304617Z ##[group]Checking out the ref
2025-07-18T22:55:53.1306441Z [command]/usr/bin/git checkout --progress --force refs/remotes/pull/109/merge
2025-07-18T22:55:53.1308930Z Note: switching to 'refs/remotes/pull/109/merge'.
2025-07-18T22:55:53.1309916Z 
2025-07-18T22:55:53.1310795Z You are in 'detached HEAD' state. You can look around, make experimental
2025-07-18T22:55:53.1312943Z changes and commit them, and you can discard any commits you make in this
2025-07-18T22:55:53.1315132Z state without impacting any branches by switching back to a branch.
2025-07-18T22:55:53.1316444Z 
2025-07-18T22:55:53.1317390Z If you want to create a new branch to retain commits you create, you may
2025-07-18T22:55:53.1320101Z do so (now or later) by using -c with the switch command. Example:
2025-07-18T22:55:53.1321448Z 
2025-07-18T22:55:53.1322175Z   git switch -c <new-branch-name>
2025-07-18T22:55:53.1323205Z 
2025-07-18T22:55:53.1323901Z Or undo this operation with:
2025-07-18T22:55:53.1325264Z 
2025-07-18T22:55:53.1325902Z   git switch -
2025-07-18T22:55:53.1326720Z 
2025-07-18T22:55:53.1328253Z Turn off this advice by setting config variable advice.detachedHead to false
2025-07-18T22:55:53.1329786Z 
2025-07-18T22:55:53.1331468Z HEAD is now at 76044d0 Merge cbfb92db94ef2ba3951fc1e1061b76a074335b3e into daf04f0268d41257ff965dc1034b7526737d46f4
2025-07-18T22:55:53.1336697Z ##[endgroup]
2025-07-18T22:55:53.1340328Z [command]/usr/bin/git log -1 --format=%H
2025-07-18T22:55:53.1342139Z 76044d01c59a523512dfd31e795709b6ed3fbcb9
2025-07-18T22:55:53.1624697Z ##[group]Run actions/setup-node@v4
2025-07-18T22:55:53.1625635Z with:
2025-07-18T22:55:53.1626348Z   node-version: 20
2025-07-18T22:55:53.1627094Z   cache: npm
2025-07-18T22:55:53.1628247Z   cache-dependency-path: frontend/package-lock.json
2025-07-18T22:55:53.1629241Z   always-auth: false
2025-07-18T22:55:53.1630016Z   check-latest: false
2025-07-18T22:55:53.1630991Z   token: ***
2025-07-18T22:55:53.1631722Z ##[endgroup]
2025-07-18T22:55:53.3418695Z Found in cache @ /opt/hostedtoolcache/node/20.19.3/x64
2025-07-18T22:55:53.3424695Z ##[group]Environment details
2025-07-18T22:55:53.7381438Z node: v20.19.3
2025-07-18T22:55:53.7384034Z npm: 10.8.2
2025-07-18T22:55:53.7386563Z yarn: 1.22.22
2025-07-18T22:55:53.7389527Z ##[endgroup]
2025-07-18T22:55:53.7407186Z [command]/opt/hostedtoolcache/node/20.19.3/x64/bin/npm config get cache
2025-07-18T22:55:53.8757408Z /home/runner/.npm
2025-07-18T22:55:54.2013151Z npm cache is not found
2025-07-18T22:55:54.2177020Z ##[group]Run npm ci
2025-07-18T22:55:54.2177906Z [36;1mnpm ci[0m
2025-07-18T22:55:54.2216182Z shell: /usr/bin/bash -e {0}
2025-07-18T22:55:54.2216852Z ##[endgroup]
2025-07-18T22:56:03.7631732Z 
2025-07-18T22:56:03.7641873Z added 423 packages, and audited 424 packages in 9s
2025-07-18T22:56:03.7642880Z 
2025-07-18T22:56:03.7643506Z 97 packages are looking for funding
2025-07-18T22:56:03.7644446Z   run `npm fund` for details
2025-07-18T22:56:03.7843813Z 
2025-07-18T22:56:03.7858597Z 7 moderate severity vulnerabilities
2025-07-18T22:56:03.7859159Z 
2025-07-18T22:56:03.7859638Z To address all issues (including breaking changes), run:
2025-07-18T22:56:03.7860254Z   npm audit fix --force
2025-07-18T22:56:03.7860536Z 
2025-07-18T22:56:03.7860791Z Run `npm audit` for details.
2025-07-18T22:56:03.8236529Z ##[group]Run npm run lint
2025-07-18T22:56:03.8236822Z [36;1mnpm run lint[0m
2025-07-18T22:56:03.8265160Z shell: /usr/bin/bash -e {0}
2025-07-18T22:56:03.8265409Z ##[endgroup]
2025-07-18T22:56:03.9428211Z 
2025-07-18T22:56:03.9429795Z > frontend@0.0.0 lint
2025-07-18T22:56:03.9430259Z > eslint .
2025-07-18T22:56:03.9430465Z 
2025-07-18T22:56:06.4424651Z ##[group]Run npx tsc --noEmit
2025-07-18T22:56:06.4425170Z [36;1mnpx tsc --noEmit[0m
2025-07-18T22:56:06.4456153Z shell: /usr/bin/bash -e {0}
2025-07-18T22:56:06.4456405Z ##[endgroup]
2025-07-18T22:56:06.9414842Z ##[group]Run npm test -- --run --coverage
2025-07-18T22:56:06.9415213Z [36;1mnpm test -- --run --coverage[0m
2025-07-18T22:56:06.9442793Z shell: /usr/bin/bash -e {0}
2025-07-18T22:56:06.9443036Z ##[endgroup]
2025-07-18T22:56:07.0748385Z 
2025-07-18T22:56:07.0749181Z > frontend@0.0.0 test
2025-07-18T22:56:07.0749946Z > vitest --run --coverage
2025-07-18T22:56:07.0750384Z 
2025-07-18T22:56:08.0074798Z 
2025-07-18T22:56:08.0101351Z [1m[7m[36m RUN [39m[27m[22m [36mv2.1.9 [39m[90m/home/runner/work/bigshot/bigshot/frontend[39m
2025-07-18T22:56:08.0102674Z       [2mCoverage enabled with [22m[33mv8[39m
2025-07-18T22:56:08.0103338Z 
2025-07-18T22:56:10.2327788Z  [31m❯[39m tests/e2e/ui-health.spec.ts [2m([22m[2m0 test[22m[2m)[22m
2025-07-18T22:56:11.1201275Z  [32m✓[39m src/config.integration.test.ts [2m([22m[2m4 tests[22m[2m)[22m[90m 5[2mms[22m[39m
2025-07-18T22:56:11.9797851Z  [32m✓[39m src/services/websocket.test.ts [2m([22m[2m10 tests[22m[2m)[22m[90m 6[2mms[22m[39m
2025-07-18T22:56:12.8634527Z  [32m✓[39m src/config.environment-detection.test.ts [2m([22m[2m5 tests[22m[2m)[22m[90m 5[2mms[22m[39m
2025-07-18T22:56:13.7467986Z  [32m✓[39m src/components/ChatInterface.contextConversion.test.tsx [2m([22m[2m5 tests[22m[2m)[22m[90m 5[2mms[22m[39m
2025-07-18T22:56:14.9068820Z  [32m✓[39m src/components/ErrorBoundary.test.tsx [2m([22m[2m7 tests[22m[2m)[22m[90m 146[2mms[22m[39m
2025-07-18T22:56:15.7831255Z  [32m✓[39m src/config.backend-resolution.test.ts [2m([22m[2m4 tests[22m[2m)[22m[90m 4[2mms[22m[39m
2025-07-18T22:56:16.6683900Z  [32m✓[39m src/config.test.ts [2m([22m[2m3 tests[22m[2m)[22m[90m 3[2mms[22m[39m
2025-07-18T22:56:17.5991635Z  [32m✓[39m src/services/chatService.test.ts [2m([22m[2m3 tests[22m[2m)[22m[90m 8[2mms[22m[39m
2025-07-18T22:56:18.8367804Z  [32m✓[39m src/components/ChatInterface.test.tsx [2m([22m[2m2 tests[22m[2m)[22m[90m 64[2mms[22m[39m
2025-07-18T22:56:18.8410345Z [90mstderr[2m | src/components/ChatInterface.test.tsx
2025-07-18T22:56:18.8413659Z [22m[39mError: AggregateError
2025-07-18T22:56:18.8416244Z     at Object.dispatchError (/home/runner/work/bigshot/bigshot/frontend/node_modules/jsdom/lib/jsdom/living/xhr/xhr-utils.js:63:19)
2025-07-18T22:56:18.8418904Z     at Request.<anonymous> (/home/runner/work/bigshot/bigshot/frontend/node_modules/jsdom/lib/jsdom/living/xhr/XMLHttpRequest-impl.js:655:18)
2025-07-18T22:56:18.8420420Z     at Request.emit (node:events:536:35)
2025-07-18T22:56:18.8421952Z     at ClientRequest.<anonymous> (/home/runner/work/bigshot/bigshot/frontend/node_modules/jsdom/lib/jsdom/living/helpers/http-request.js:127:14)
2025-07-18T22:56:18.8423451Z     at ClientRequest.emit (node:events:524:28)
2025-07-18T22:56:18.8428511Z     at emitErrorEvent (node:_http_client:101:11)
2025-07-18T22:56:18.8438332Z     at Socket.socketErrorListener (node:_http_client:504:5)
2025-07-18T22:56:18.8439018Z     at Socket.emit (node:events:524:28)
2025-07-18T22:56:18.8439611Z     at emitErrorNT (node:internal/streams/destroy:169:8)
2025-07-18T22:56:18.8440587Z     at emitErrorCloseNT (node:internal/streams/destroy:128:3) [90mundefined[39m
2025-07-18T22:56:18.8441461Z Failed to check service status: AxiosError: Network Error
2025-07-18T22:56:18.8443018Z     at XMLHttpRequest.handleError [90m(file:///home/runner/work/bigshot/bigshot/frontend/[39mnode_modules/[4maxios[24m/lib/adapters/xhr.js:110:14[90m)[39m
2025-07-18T22:56:18.8445583Z     at XMLHttpRequest.invokeTheCallbackFunction [90m(/home/runner/work/bigshot/bigshot/frontend/[39mnode_modules/[4mjsdom[24m/lib/jsdom/living/generated/EventHandlerNonNull.js:14:28[90m)[39m
2025-07-18T22:56:18.8448480Z     at XMLHttpRequest.<anonymous> [90m(/home/runner/work/bigshot/bigshot/frontend/[39mnode_modules/[4mjsdom[24m/lib/jsdom/living/helpers/create-event-accessor.js:35:32[90m)[39m
2025-07-18T22:56:18.8451428Z     at innerInvokeEventListeners [90m(/home/runner/work/bigshot/bigshot/frontend/[39mnode_modules/[4mjsdom[24m/lib/jsdom/living/events/EventTarget-impl.js:350:25[90m)[39m
2025-07-18T22:56:18.8453875Z     at invokeEventListeners [90m(/home/runner/work/bigshot/bigshot/frontend/[39mnode_modules/[4mjsdom[24m/lib/jsdom/living/events/EventTarget-impl.js:286:3[90m)[39m
2025-07-18T22:56:18.8456400Z     at XMLHttpRequestImpl._dispatch [90m(/home/runner/work/bigshot/bigshot/frontend/[39mnode_modules/[4mjsdom[24m/lib/jsdom/living/events/EventTarget-impl.js:233:9[90m)[39m
2025-07-18T22:56:18.8458849Z     at fireAnEvent [90m(/home/runner/work/bigshot/bigshot/frontend/[39mnode_modules/[4mjsdom[24m/lib/jsdom/living/helpers/events.js:18:36[90m)[39m
2025-07-18T22:56:18.8460900Z     at requestErrorSteps [90m(/home/runner/work/bigshot/bigshot/frontend/[39mnode_modules/[4mjsdom[24m/lib/jsdom/living/xhr/xhr-utils.js:131:3[90m)[39m
2025-07-18T22:56:18.8463026Z     at Object.dispatchError [90m(/home/runner/work/bigshot/bigshot/frontend/[39mnode_modules/[4mjsdom[24m/lib/jsdom/living/xhr/xhr-utils.js:60:3[90m)[39m
2025-07-18T22:56:18.8465246Z     at Request.<anonymous> [90m(/home/runner/work/bigshot/bigshot/frontend/[39mnode_modules/[4mjsdom[24m/lib/jsdom/living/xhr/XMLHttpRequest-impl.js:655:18[90m)[39m
2025-07-18T22:56:18.8467723Z     at Axios.request [90m(file:///home/runner/work/bigshot/bigshot/frontend/[39mnode_modules/[4maxios[24m/lib/core/Axios.js:45:41[90m)[39m
2025-07-18T22:56:18.8469254Z [90m    at processTicksAndRejections (node:internal/process/task_queues:95:5)[39m
2025-07-18T22:56:18.8470700Z     at ChatService.getStatus [90m(/home/runner/work/bigshot/bigshot/frontend/[39msrc/services/chatService.ts:121:22[90m)[39m
2025-07-18T22:56:18.8472435Z     at checkServiceStatus [90m(/home/runner/work/bigshot/bigshot/frontend/[39msrc/components/ChatInterface.tsx:33:22[90m)[39m {
2025-07-18T22:56:18.8473463Z   code: [32m'ERR_NETWORK'[39m,
2025-07-18T22:56:18.8473849Z   config: {
2025-07-18T22:56:18.8474157Z     transitional: {
2025-07-18T22:56:18.8474643Z       silentJSONParsing: [33mtrue[39m,
2025-07-18T22:56:18.8475214Z       forcedJSONParsing: [33mtrue[39m,
2025-07-18T22:56:18.8475775Z       clarifyTimeoutError: [33mfalse[39m
2025-07-18T22:56:18.8476200Z     },
2025-07-18T22:56:18.8476768Z     adapter: [ [32m'xhr'[39m, [32m'http'[39m, [32m'fetch'[39m ],
2025-07-18T22:56:18.8477767Z     transformRequest: [ [36m[Function: transformRequest][39m ],
2025-07-18T22:56:18.8478663Z     transformResponse: [ [36m[Function: transformResponse][39m ],
2025-07-18T22:56:18.8479288Z     timeout: [33m0[39m,
2025-07-18T22:56:18.8479798Z     xsrfCookieName: [32m'XSRF-TOKEN'[39m,
2025-07-18T22:56:18.8480389Z     xsrfHeaderName: [32m'X-XSRF-TOKEN'[39m,
2025-07-18T22:56:18.8480946Z     maxContentLength: [33m-1[39m,
2025-07-18T22:56:18.8481444Z     maxBodyLength: [33m-1[39m,
2025-07-18T22:56:18.8482220Z     env: { FormData: [36m[Function [FormData]][39m, Blob: [36m[class Blob][39m },
2025-07-18T22:56:18.8483113Z     validateStatus: [36m[Function: validateStatus][39m,
2025-07-18T22:56:18.8483692Z     headers: Object [AxiosHeaders] {
2025-07-18T22:56:18.8484342Z       Accept: [32m'application/json, text/plain, */*'[39m,
2025-07-18T22:56:18.8485052Z       [32m'Content-Type'[39m: [90mundefined[39m,
2025-07-18T22:56:18.8485808Z       Authorization: [32m'***'[39m
2025-07-18T22:56:18.8486213Z     },
2025-07-18T22:56:18.8486573Z     method: [32m'get'[39m,
2025-07-18T22:56:18.8487081Z     url: [32m'/api/v1/chat/status'[39m,
2025-07-18T22:56:18.8487809Z     allowAbsoluteUrls: [33mtrue[39m,
2025-07-18T22:56:18.8488323Z     data: [90mundefined[39m
2025-07-18T22:56:18.8488664Z   },
2025-07-18T22:56:18.8488965Z   request: XMLHttpRequest {}
2025-07-18T22:56:18.8489328Z }
2025-07-18T22:56:18.8489629Z Error: AggregateError
2025-07-18T22:56:18.8490639Z     at Object.dispatchError (/home/runner/work/bigshot/bigshot/frontend/node_modules/jsdom/lib/jsdom/living/xhr/xhr-utils.js:63:19)
2025-07-18T22:56:18.8492602Z     at Request.<anonymous> (/home/runner/work/bigshot/bigshot/frontend/node_modules/jsdom/lib/jsdom/living/xhr/XMLHttpRequest-impl.js:655:18)
2025-07-18T22:56:18.8493735Z     at Request.emit (node:events:536:35)
2025-07-18T22:56:18.8494918Z     at ClientRequest.<anonymous> (/home/runner/work/bigshot/bigshot/frontend/node_modules/jsdom/lib/jsdom/living/helpers/http-request.js:127:14)
2025-07-18T22:56:18.8496091Z     at ClientRequest.emit (node:events:524:28)
2025-07-18T22:56:18.8496649Z     at emitErrorEvent (node:_http_client:101:11)
2025-07-18T22:56:18.8497265Z     at Socket.socketErrorListener (node:_http_client:504:5)
2025-07-18T22:56:18.8498077Z     at Socket.emit (node:events:524:28)
2025-07-18T22:56:18.8498675Z     at emitErrorNT (node:internal/streams/destroy:169:8)
2025-07-18T22:56:18.8499615Z     at emitErrorCloseNT (node:internal/streams/destroy:128:3) [90mundefined[39m
2025-07-18T22:56:18.8500441Z Failed to load context: AxiosError: Network Error
2025-07-18T22:56:18.8502014Z     at XMLHttpRequest.handleError [90m(file:///home/runner/work/bigshot/bigshot/frontend/[39mnode_modules/[4maxios[24m/lib/adapters/xhr.js:110:14[90m)[39m
2025-07-18T22:56:18.8504611Z     at XMLHttpRequest.invokeTheCallbackFunction [90m(/home/runner/work/bigshot/bigshot/frontend/[39mnode_modules/[4mjsdom[24m/lib/jsdom/living/generated/EventHandlerNonNull.js:14:28[90m)[39m
2025-07-18T22:56:18.8507660Z     at XMLHttpRequest.<anonymous> [90m(/home/runner/work/bigshot/bigshot/frontend/[39mnode_modules/[4mjsdom[24m/lib/jsdom/living/helpers/create-event-accessor.js:35:32[90m)[39m
2025-07-18T22:56:18.8510161Z     at innerInvokeEventListeners [90m(/home/runner/work/bigshot/bigshot/frontend/[39mnode_modules/[4mjsdom[24m/lib/jsdom/living/events/EventTarget-impl.js:350:25[90m)[39m
2025-07-18T22:56:18.8512534Z     at invokeEventListeners [90m(/home/runner/work/bigshot/bigshot/frontend/[39mnode_modules/[4mjsdom[24m/lib/jsdom/living/events/EventTarget-impl.js:286:3[90m)[39m
2025-07-18T22:56:18.8515008Z     at XMLHttpRequestImpl._dispatch [90m(/home/runner/work/bigshot/bigshot/frontend/[39mnode_modules/[4mjsdom[24m/lib/jsdom/living/events/EventTarget-impl.js:233:9[90m)[39m
2025-07-18T22:56:18.8517183Z     at fireAnEvent [90m(/home/runner/work/bigshot/bigshot/frontend/[39mnode_modules/[4mjsdom[24m/lib/jsdom/living/helpers/events.js:18:36[90m)[39m
2025-07-18T22:56:18.8519449Z     at requestErrorSteps [90m(/home/runner/work/bigshot/bigshot/frontend/[39mnode_modules/[4mjsdom[24m/lib/jsdom/living/xhr/xhr-utils.js:131:3[90m)[39m
2025-07-18T22:56:18.8521607Z     at Object.dispatchError [90m(/home/runner/work/bigshot/bigshot/frontend/[39mnode_modules/[4mjsdom[24m/lib/jsdom/living/xhr/xhr-utils.js:60:3[90m)[39m
2025-07-18T22:56:18.8523860Z     at Request.<anonymous> [90m(/home/runner/work/bigshot/bigshot/frontend/[39mnode_modules/[4mjsdom[24m/lib/jsdom/living/xhr/XMLHttpRequest-impl.js:655:18[90m)[39m
2025-07-18T22:56:18.8526000Z     at Axios.request [90m(file:///home/runner/work/bigshot/bigshot/frontend/[39mnode_modules/[4maxios[24m/lib/core/Axios.js:45:41[90m)[39m
2025-07-18T22:56:18.8527740Z [90m    at processTicksAndRejections (node:internal/process/task_queues:95:5)[39m
2025-07-18T22:56:18.8529272Z     at ChatService.getContext [90m(/home/runner/work/bigshot/bigshot/frontend/[39msrc/services/chatService.ts:132:22[90m)[39m
2025-07-18T22:56:18.8531013Z     at loadContext [90m(/home/runner/work/bigshot/bigshot/frontend/[39msrc/components/ChatInterface.tsx:43:27[90m)[39m {
2025-07-18T22:56:18.8532062Z   code: [32m'ERR_NETWORK'[39m,
2025-07-18T22:56:18.8532450Z   config: {
2025-07-18T22:56:18.8532755Z     transitional: {
2025-07-18T22:56:18.8533236Z       silentJSONParsing: [33mtrue[39m,
2025-07-18T22:56:18.8533826Z       forcedJSONParsing: [33mtrue[39m,
2025-07-18T22:56:18.8534417Z       clarifyTimeoutError: [33mfalse[39m
2025-07-18T22:56:18.8534847Z     },
2025-07-18T22:56:18.8535435Z     adapter: [ [32m'xhr'[39m, [32m'http'[39m, [32m'fetch'[39m ],
2025-07-18T22:56:18.8536482Z     transformRequest: [ [36m[Function: transformRequest][39m ],
2025-07-18T22:56:18.8537395Z     transformResponse: [ [36m[Function: transformResponse][39m ],
2025-07-18T22:56:18.8538209Z     timeout: [33m0[39m,
2025-07-18T22:56:18.8538752Z     xsrfCookieName: [32m'XSRF-TOKEN'[39m,
2025-07-18T22:56:18.8539358Z     xsrfHeaderName: [32m'X-XSRF-TOKEN'[39m,
2025-07-18T22:56:18.8539943Z     maxContentLength: [33m-1[39m,
2025-07-18T22:56:18.8540469Z     maxBodyLength: [33m-1[39m,
2025-07-18T22:56:18.8541267Z     env: { FormData: [36m[Function [FormData]][39m, Blob: [36m[class Blob][39m },
2025-07-18T22:56:18.8542145Z     validateStatus: [36m[Function: validateStatus][39m,
2025-07-18T22:56:18.8542718Z     headers: Object [AxiosHeaders] {
2025-07-18T22:56:18.8543400Z       Accept: [32m'application/json, text/plain, */*'[39m,
2025-07-18T22:56:18.8544112Z       [32m'Content-Type'[39m: [90mundefined[39m,
2025-07-18T22:56:18.8544832Z       Authorization: [32m'***'[39m
2025-07-18T22:56:18.8545232Z     },
2025-07-18T22:56:18.8545608Z     method: [32m'get'[39m,
2025-07-18T22:56:18.8546134Z     url: [32m'/api/v1/chat/context'[39m,
2025-07-18T22:56:18.8546736Z     allowAbsoluteUrls: [33mtrue[39m,
2025-07-18T22:56:18.8547438Z     data: [90mundefined[39m
2025-07-18T22:56:18.8547979Z   },
2025-07-18T22:56:18.8548290Z   request: XMLHttpRequest {}
2025-07-18T22:56:18.8548661Z }
2025-07-18T22:56:18.8548973Z Error: AggregateError
2025-07-18T22:56:18.8550052Z     at Object.dispatchError (/home/runner/work/bigshot/bigshot/frontend/node_modules/jsdom/lib/jsdom/living/xhr/xhr-utils.js:63:19)
2025-07-18T22:56:18.8551845Z     at Request.<anonymous> (/home/runner/work/bigshot/bigshot/frontend/node_modules/jsdom/lib/jsdom/living/xhr/XMLHttpRequest-impl.js:655:18)
2025-07-18T22:56:18.8553003Z     at Request.emit (node:events:536:35)
2025-07-18T22:56:18.8554238Z     at ClientRequest.<anonymous> (/home/runner/work/bigshot/bigshot/frontend/node_modules/jsdom/lib/jsdom/living/helpers/http-request.js:127:14)
2025-07-18T22:56:18.8555442Z     at ClientRequest.emit (node:events:524:28)
2025-07-18T22:56:18.8556062Z     at emitErrorEvent (node:_http_client:101:11)
2025-07-18T22:56:18.8556697Z     at Socket.socketErrorListener (node:_http_client:504:5)
2025-07-18T22:56:18.8557306Z     at Socket.emit (node:events:524:28)
2025-07-18T22:56:18.8558040Z     at emitErrorNT (node:internal/streams/destroy:169:8)
2025-07-18T22:56:18.8558979Z     at emitErrorCloseNT (node:internal/streams/destroy:128:3) [90mundefined[39m
2025-07-18T22:56:18.8559853Z Failed to check service status: AxiosError: Network Error
2025-07-18T22:56:18.8561462Z     at XMLHttpRequest.handleError [90m(file:///home/runner/work/bigshot/bigshot/frontend/[39mnode_modules/[4maxios[24m/lib/adapters/xhr.js:110:14[90m)[39m
2025-07-18T22:56:18.8564005Z     at XMLHttpRequest.invokeTheCallbackFunction [90m(/home/runner/work/bigshot/bigshot/frontend/[39mnode_modules/[4mjsdom[24m/lib/jsdom/living/generated/EventHandlerNonNull.js:14:28[90m)[39m
2025-07-18T22:56:18.8566706Z     at XMLHttpRequest.<anonymous> [90m(/home/runner/work/bigshot/bigshot/frontend/[39mnode_modules/[4mjsdom[24m/lib/jsdom/living/helpers/create-event-accessor.js:35:32[90m)[39m
2025-07-18T22:56:18.8569404Z     at innerInvokeEventListeners [90m(/home/runner/work/bigshot/bigshot/frontend/[39mnode_modules/[4mjsdom[24m/lib/jsdom/living/events/EventTarget-impl.js:350:25[90m)[39m
2025-07-18T22:56:18.8571849Z     at invokeEventListeners [90m(/home/runner/work/bigshot/bigshot/frontend/[39mnode_modules/[4mjsdom[24m/lib/jsdom/living/events/EventTarget-impl.js:286:3[90m)[39m
2025-07-18T22:56:18.8574296Z     at XMLHttpRequestImpl._dispatch [90m(/home/runner/work/bigshot/bigshot/frontend/[39mnode_modules/[4mjsdom[24m/lib/jsdom/living/events/EventTarget-impl.js:233:9[90m)[39m
2025-07-18T22:56:18.8576575Z     at fireAnEvent [90m(/home/runner/work/bigshot/bigshot/frontend/[39mnode_modules/[4mjsdom[24m/lib/jsdom/living/helpers/events.js:18:36[90m)[39m
2025-07-18T22:56:18.8584804Z     at requestErrorSteps [90m(/home/runner/work/bigshot/bigshot/frontend/[39mnode_modules/[4mjsdom[24m/lib/jsdom/living/xhr/xhr-utils.js:131:3[90m)[39m
2025-07-18T22:56:18.8587044Z     at Object.dispatchError [90m(/home/runner/work/bigshot/bigshot/frontend/[39mnode_modules/[4mjsdom[24m/lib/jsdom/living/xhr/xhr-utils.js:60:3[90m)[39m
2025-07-18T22:56:18.8589506Z     at Request.<anonymous> [90m(/home/runner/work/bigshot/bigshot/frontend/[39mnode_modules/[4mjsdom[24m/lib/jsdom/living/xhr/XMLHttpRequest-impl.js:655:18[90m)[39m
2025-07-18T22:56:18.8591628Z     at Axios.request [90m(file:///home/runner/work/bigshot/bigshot/frontend/[39mnode_modules/[4maxios[24m/lib/core/Axios.js:45:41[90m)[39m
2025-07-18T22:56:18.8593182Z [90m    at processTicksAndRejections (node:internal/process/task_queues:95:5)[39m
2025-07-18T22:56:18.8594692Z     at ChatService.getStatus [90m(/home/runner/work/bigshot/bigshot/frontend/[39msrc/services/chatService.ts:121:22[90m)[39m
2025-07-18T22:56:18.8596531Z     at checkServiceStatus [90m(/home/runner/work/bigshot/bigshot/frontend/[39msrc/components/ChatInterface.tsx:33:22[90m)[39m {
2025-07-18T22:56:18.8597807Z   code: [32m'ERR_NETWORK'[39m,
2025-07-18T22:56:18.8598383Z   config: {
2025-07-18T22:56:18.8598709Z     transitional: {
2025-07-18T22:56:18.8599213Z       silentJSONParsing: [33mtrue[39m,
2025-07-18T22:56:18.8599803Z       forcedJSONParsing: [33mtrue[39m,
2025-07-18T22:56:18.8600391Z       clarifyTimeoutError: [33mfalse[39m
2025-07-18T22:56:18.8600827Z     },
2025-07-18T22:56:18.8601410Z     adapter: [ [32m'xhr'[39m, [32m'http'[39m, [32m'fetch'[39m ],
2025-07-18T22:56:18.8602264Z     transformRequest: [ [36m[Function: transformRequest][39m ],
2025-07-18T22:56:18.8603156Z     transformResponse: [ [36m[Function: transformResponse][39m ],
2025-07-18T22:56:18.8603791Z     timeout: [33m0[39m,
2025-07-18T22:56:18.8604309Z     xsrfCookieName: [32m'XSRF-TOKEN'[39m,
2025-07-18T22:56:18.8604911Z     xsrfHeaderName: [32m'X-XSRF-TOKEN'[39m,
2025-07-18T22:56:18.8605500Z     maxContentLength: [33m-1[39m,
2025-07-18T22:56:18.8606023Z     maxBodyLength: [33m-1[39m,
2025-07-18T22:56:18.8606817Z     env: { FormData: [36m[Function [FormData]][39m, Blob: [36m[class Blob][39m },
2025-07-18T22:56:18.8607876Z     validateStatus: [36m[Function: validateStatus][39m,
2025-07-18T22:56:18.8608466Z     headers: Object [AxiosHeaders] {
2025-07-18T22:56:18.8609137Z       Accept: [32m'application/json, text/plain, */*'[39m,
2025-07-18T22:56:18.8609850Z       [32m'Content-Type'[39m: [90mundefined[39m,
2025-07-18T22:56:18.8610562Z       Authorization: [32m'***'[39m
2025-07-18T22:56:18.8610968Z     },
2025-07-18T22:56:18.8611335Z     method: [32m'get'[39m,
2025-07-18T22:56:18.8611849Z     url: [32m'/api/v1/chat/status'[39m,
2025-07-18T22:56:18.8612417Z     allowAbsoluteUrls: [33mtrue[39m,
2025-07-18T22:56:18.8612915Z     data: [90mundefined[39m
2025-07-18T22:56:18.8613269Z   },
2025-07-18T22:56:18.8613587Z   request: XMLHttpRequest {}
2025-07-18T22:56:18.8613972Z }
2025-07-18T22:56:18.8614294Z Error: AggregateError
2025-07-18T22:56:18.8615390Z     at Object.dispatchError (/home/runner/work/bigshot/bigshot/frontend/node_modules/jsdom/lib/jsdom/living/xhr/xhr-utils.js:63:19)
2025-07-18T22:56:18.8617238Z     at Request.<anonymous> (/home/runner/work/bigshot/bigshot/frontend/node_modules/jsdom/lib/jsdom/living/xhr/XMLHttpRequest-impl.js:655:18)
2025-07-18T22:56:18.8618552Z     at Request.emit (node:events:536:35)
2025-07-18T22:56:18.8619809Z     at ClientRequest.<anonymous> (/home/runner/work/bigshot/bigshot/frontend/node_modules/jsdom/lib/jsdom/living/helpers/http-request.js:127:14)
2025-07-18T22:56:18.8621011Z     at ClientRequest.emit (node:events:524:28)
2025-07-18T22:56:18.8621571Z     at emitErrorEvent (node:_http_client:101:11)
2025-07-18T22:56:18.8622215Z     at Socket.socketErrorListener (node:_http_client:504:5)
2025-07-18T22:56:18.8622821Z     at Socket.emit (node:events:524:28)
2025-07-18T22:56:18.8623396Z     at emitErrorNT (node:internal/streams/destroy:169:8)
2025-07-18T22:56:18.8624526Z     at emitErrorCloseNT (node:internal/streams/destroy:128:3) [90mundefined[39m
2025-07-18T22:56:18.8625381Z Failed to load context: AxiosError: Network Error
2025-07-18T22:56:18.8626961Z     at XMLHttpRequest.handleError [90m(file:///home/runner/work/bigshot/bigshot/frontend/[39mnode_modules/[4maxios[24m/lib/adapters/xhr.js:110:14[90m)[39m
2025-07-18T22:56:18.8629710Z     at XMLHttpRequest.invokeTheCallbackFunction [90m(/home/runner/work/bigshot/bigshot/frontend/[39mnode_modules/[4mjsdom[24m/lib/jsdom/living/generated/EventHandlerNonNull.js:14:28[90m)[39m
2025-07-18T22:56:18.8632449Z     at XMLHttpRequest.<anonymous> [90m(/home/runner/work/bigshot/bigshot/frontend/[39mnode_modules/[4mjsdom[24m/lib/jsdom/living/helpers/create-event-accessor.js:35:32[90m)[39m
2025-07-18T22:56:18.8635028Z     at innerInvokeEventListeners [90m(/home/runner/work/bigshot/bigshot/frontend/[39mnode_modules/[4mjsdom[24m/lib/jsdom/living/events/EventTarget-impl.js:350:25[90m)[39m
2025-07-18T22:56:18.8637619Z     at invokeEventListeners [90m(/home/runner/work/bigshot/bigshot/frontend/[39mnode_modules/[4mjsdom[24m/lib/jsdom/living/events/EventTarget-impl.js:286:3[90m)[39m
2025-07-18T22:56:18.8640170Z     at XMLHttpRequestImpl._dispatch [90m(/home/runner/work/bigshot/bigshot/frontend/[39mnode_modules/[4mjsdom[24m/lib/jsdom/living/events/EventTarget-impl.js:233:9[90m)[39m
2025-07-18T22:56:18.8642446Z     at fireAnEvent [90m(/home/runner/work/bigshot/bigshot/frontend/[39mnode_modules/[4mjsdom[24m/lib/jsdom/living/helpers/events.js:18:36[90m)[39m
2025-07-18T22:56:18.8644567Z     at requestErrorSteps [90m(/home/runner/work/bigshot/bigshot/frontend/[39mnode_modules/[4mjsdom[24m/lib/jsdom/living/xhr/xhr-utils.js:131:3[90m)[39m
2025-07-18T22:56:18.8646711Z     at Object.dispatchError [90m(/home/runner/work/bigshot/bigshot/frontend/[39mnode_modules/[4mjsdom[24m/lib/jsdom/living/xhr/xhr-utils.js:60:3[90m)[39m
2025-07-18T22:56:18.8649221Z     at Request.<anonymous> [90m(/home/runner/work/bigshot/bigshot/frontend/[39mnode_modules/[4mjsdom[24m/lib/jsdom/living/xhr/XMLHttpRequest-impl.js:655:18[90m)[39m
2025-07-18T22:56:18.8651369Z     at Axios.request [90m(file:///home/runner/work/bigshot/bigshot/frontend/[39mnode_modules/[4maxios[24m/lib/core/Axios.js:45:41[90m)[39m
2025-07-18T22:56:18.8652927Z [90m    at processTicksAndRejections (node:internal/process/task_queues:95:5)[39m
2025-07-18T22:56:18.8654404Z     at ChatService.getContext [90m(/home/runner/work/bigshot/bigshot/frontend/[39msrc/services/chatService.ts:132:22[90m)[39m
2025-07-18T22:56:18.8656182Z     at loadContext [90m(/home/runner/work/bigshot/bigshot/frontend/[39msrc/components/ChatInterface.tsx:43:27[90m)[39m {
2025-07-18T22:56:18.8657255Z   code: [32m'ERR_NETWORK'[39m,
2025-07-18T22:56:18.8657785Z   config: {
2025-07-18T22:56:18.8658092Z     transitional: {
2025-07-18T22:56:18.8658582Z       silentJSONParsing: [33mtrue[39m,
2025-07-18T22:56:18.8659164Z       forcedJSONParsing: [33mtrue[39m,
2025-07-18T22:56:18.8659757Z       clarifyTimeoutError: [33mfalse[39m
2025-07-18T22:56:18.8660189Z     },
2025-07-18T22:56:18.8660759Z     adapter: [ [32m'xhr'[39m, [32m'http'[39m, [32m'fetch'[39m ],
2025-07-18T22:56:18.8661600Z     transformRequest: [ [36m[Function: transformRequest][39m ],
2025-07-18T22:56:18.8662487Z     transformResponse: [ [36m[Function: transformResponse][39m ],
2025-07-18T22:56:18.8663115Z     timeout: [33m0[39m,
2025-07-18T22:56:18.8663634Z     xsrfCookieName: [32m'XSRF-TOKEN'[39m,
2025-07-18T22:56:18.8664243Z     xsrfHeaderName: [32m'X-XSRF-TOKEN'[39m,
2025-07-18T22:56:18.8664810Z     maxContentLength: [33m-1[39m,
2025-07-18T22:56:18.8665329Z     maxBodyLength: [33m-1[39m,
2025-07-18T22:56:18.8666130Z     env: { FormData: [36m[Function [FormData]][39m, Blob: [36m[class Blob][39m },
2025-07-18T22:56:18.8667026Z     validateStatus: [36m[Function: validateStatus][39m,
2025-07-18T22:56:18.8667776Z     headers: Object [AxiosHeaders] {
2025-07-18T22:56:18.8668666Z       Accept: [32m'application/json, text/plain, */*'[39m,
2025-07-18T22:56:18.8669394Z       [32m'Content-Type'[39m: [90mundefined[39m,
2025-07-18T22:56:18.8670127Z       Authorization: [32m'***'[39m
2025-07-18T22:56:18.8670552Z     },
2025-07-18T22:56:18.8670908Z     method: [32m'get'[39m,
2025-07-18T22:56:18.8671435Z     url: [32m'/api/v1/chat/context'[39m,
2025-07-18T22:56:18.8671998Z     allowAbsoluteUrls: [33mtrue[39m,
2025-07-18T22:56:18.8672496Z     data: [90mundefined[39m
2025-07-18T22:56:18.8672861Z   },
2025-07-18T22:56:18.8673163Z   request: XMLHttpRequest {}
2025-07-18T22:56:18.8673531Z }
2025-07-18T22:56:18.8673681Z 
2025-07-18T22:56:20.0042605Z  [32m✓[39m src/components/monitoring/ConfigurationManagement.test.tsx [2m([22m[2m2 tests[22m[2m)[22m[90m 36[2mms[22m[39m
2025-07-18T22:56:21.1386297Z  [32m✓[39m src/components/chat/ChatInterface.test.tsx [2m([22m[2m2 tests[22m[2m)[22m[90m 37[2mms[22m[39m
2025-07-18T22:56:22.6404037Z  [32m✓[39m src/App.test.tsx [2m([22m[2m1 test[22m[2m)[22m[90m 59[2mms[22m[39m
2025-07-18T22:56:22.6512000Z [90mstderr[2m | VirtualConsole.<anonymous> (/home/runner/work/bigshot/bigshot/frontend/node_modules/jsdom/lib/jsdom/virtual-console.js:29:45)
2025-07-18T22:56:22.6540788Z [22m[39mError: AggregateError
2025-07-18T22:56:22.6545061Z     at Object.dispatchError (/home/runner/work/bigshot/bigshot/frontend/node_modules/jsdom/lib/jsdom/living/xhr/xhr-utils.js:63:19)
2025-07-18T22:56:22.6550078Z     at Request.<anonymous> (/home/runner/work/bigshot/bigshot/frontend/node_modules/jsdom/lib/jsdom/living/xhr/XMLHttpRequest-impl.js:655:18)
2025-07-18T22:56:22.6554310Z     at Request.emit (node:events:536:35)
2025-07-18T22:56:22.6557868Z     at ClientRequest.<anonymous> (/home/runner/work/bigshot/bigshot/frontend/node_modules/jsdom/lib/jsdom/living/helpers/http-request.js:127:14)
2025-07-18T22:56:22.6561091Z     at ClientRequest.emit (node:events:524:28)
2025-07-18T22:56:22.6563527Z     at emitErrorEvent (node:_http_client:101:11)
2025-07-18T22:56:22.6566054Z     at Socket.socketErrorListener (node:_http_client:504:5)
2025-07-18T22:56:22.6568759Z     at Socket.emit (node:events:524:28)
2025-07-18T22:56:22.6570718Z     at emitErrorNT (node:internal/streams/destroy:169:8)
2025-07-18T22:56:22.6572868Z     at emitErrorCloseNT (node:internal/streams/destroy:128:3) [90mundefined[39m
2025-07-18T22:56:22.6574577Z 
2025-07-18T22:56:23.0129392Z 
2025-07-18T22:56:23.0140653Z [31m⎯⎯⎯⎯⎯⎯[1m[7m Failed Suites 1 [27m[22m⎯⎯⎯⎯⎯⎯⎯[39m
2025-07-18T22:56:23.0142094Z 
2025-07-18T22:56:23.0145616Z [31m[1m[7m FAIL [27m[22m[39m tests/e2e/ui-health.spec.ts[2m [ tests/e2e/ui-health.spec.ts ][22m
2025-07-18T22:56:23.0166263Z [31m[1mError[22m: Playwright Test did not expect test() to be called here.
2025-07-18T22:56:23.0168365Z Most common reasons include:
2025-07-18T22:56:23.0169002Z - You are calling test() in a configuration file.
2025-07-18T22:56:23.0169900Z - You are calling test() in a file that is imported by the configuration file.
2025-07-18T22:56:23.0170975Z - You have two different versions of @playwright/test. This usually happens
2025-07-18T22:56:23.0172203Z   when one of the dependencies in your package.json depends on @playwright/test.[39m
2025-07-18T22:56:23.0173823Z [90m [2m❯[22m TestTypeImpl._currentSuite node_modules/playwright/lib/common/testType.js:[2m74:13[22m[39m
2025-07-18T22:56:23.0176900Z [90m [2m❯[22m TestTypeImpl._createTest node_modules/playwright/lib/common/testType.js:[2m87:24[22m[39m
2025-07-18T22:56:23.0180113Z [90m [2m❯[22m Module.<anonymous> node_modules/playwright/lib/transform/transform.js:[2m275:12[22m[39m
2025-07-18T22:56:23.0183202Z [36m [2m❯[22m tests/e2e/ui-health.spec.ts:[2m219:1[22m[39m
2025-07-18T22:56:23.0438170Z     [90m217| [39m}
2025-07-18T22:56:23.0440290Z     [90m218| [39m
2025-07-18T22:56:23.0443574Z     [90m219| [39m[34mtest[39m([32m'should login, pass verification, and capture healthy dashboard s[39m…
2025-07-18T22:56:23.0444395Z     [90m   | [39m[31m^[39m
2025-07-18T22:56:23.0445694Z     [90m220| [39m  console[33m.[39m[34mlog[39m([32m'🚀 Starting UI health check test...'[39m)[33m;[39m
2025-07-18T22:56:23.0446495Z     [90m221| [39m  
2025-07-18T22:56:23.0446706Z 
2025-07-18T22:56:23.0447128Z [31m[2m⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯[1/1]⎯[22m[39m
2025-07-18T22:56:23.0447634Z 
2025-07-18T22:56:23.0471450Z [2m Test Files [22m [1m[31m1 failed[39m[22m[2m | [22m[1m[32m12 passed[39m[22m[90m (13)[39m
2025-07-18T22:56:23.0474862Z [2m      Tests [22m [1m[32m48 passed[39m[22m[90m (48)[39m
2025-07-18T22:56:23.0476205Z [2m   Start at [22m 22:56:07
2025-07-18T22:56:23.0479478Z [2m   Duration [22m 15.01s[2m (transform 438ms, setup 2.02s, collect 1.63s, tests 378ms, environment 6.07s, prepare 930ms)[22m
2025-07-18T22:56:23.0480792Z 
2025-07-18T22:56:23.0491687Z 
2025-07-18T22:56:23.0547399Z ##[error]Error: Playwright Test did not expect test() to be called here.
Most common reasons include:
- You are calling test() in a configuration file.
- You are calling test() in a file that is imported by the configuration file.
- You have two different versions of @playwright/test. This usually happens
  when one of the dependencies in your package.json depends on @playwright/test.
 ❯ TestTypeImpl._currentSuite node_modules/playwright/lib/common/testType.js:74:13
 ❯ TestTypeImpl._createTest node_modules/playwright/lib/common/testType.js:87:24
 ❯ Module.<anonymous> node_modules/playwright/lib/transform/transform.js:275:12
 ❯ tests/e2e/ui-health.spec.ts:219:1


2025-07-18T22:56:23.0892662Z ##[error]Process completed with exit code 1.
2025-07-18T22:56:23.1020682Z Post job cleanup.
2025-07-18T22:56:23.1983946Z [command]/usr/bin/git version
2025-07-18T22:56:23.2032392Z git version 2.50.1
2025-07-18T22:56:23.2079208Z Temporarily overriding HOME='/home/runner/work/_temp/a1957446-9055-4d84-95ef-51ddbd481cd6' before making global git config changes
2025-07-18T22:56:23.2080769Z Adding repository directory to the temporary git global config as a safe directory
2025-07-18T22:56:23.2085002Z [command]/usr/bin/git config --global --add safe.directory /home/runner/work/bigshot/bigshot
2025-07-18T22:56:23.2121034Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
2025-07-18T22:56:23.2155628Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
2025-07-18T22:56:23.2391306Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2025-07-18T22:56:23.2413819Z http.https://github.com/.extraheader
2025-07-18T22:56:23.2428937Z [command]/usr/bin/git config --local --unset-all http.https://github.com/.extraheader
2025-07-18T22:56:23.2461928Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
2025-07-18T22:56:23.2912118Z Cleaning up orphan processes
```