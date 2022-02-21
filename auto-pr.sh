#!/bin/bash

collectorversion="5.0.0"
echo ""
read -n 1 -p "PR type? ([n]ew entry/new [f]ile/real [V]alues/[c]orrections/feature [r]emoval/f[l][a]g removal (by flag/feature)/[e]vent adaptation) " prtype
[[ ! -z $prtype ]] && echo ""
case $prtype in 
  [Ee*] ) cat=api; category=API;;
  * )
    read -n 1 -p "Category? ([A]pi/[c]ss/[h]tml/h[t]tp/[j]avascript/[s]vg/web[d]river/web[e]xtensions) " catopt
    [[ ! -z $catopt ]] && echo ""
    case $catopt in
      [Cc*] ) read -n 1 -p "Sub-category? ([a]t-rules/[P]roperties/[s]electors/[t]ypes) " subcat;
        echo "";
        case $subcat in
          [Aa*] ) cat=css/at-rules; category="CSS @rule";;
          [Ss*] ) cat=css/selectors; category="CSS selector";;
          [Tt*] ) cat=css/types; category="CSS type";;
          * ) cat=css/properties; category="CSS property";;
        esac;;
      [Hh*] ) read -n 1 -p "Sub-category? ([E]lements/[m]anifest/[o]ther) " subcat;
        echo "";
        case $subcat in
          [Mm*] ) cat=html/manifest; category="HTML manifest";;
          [Oo*] ) cat=html; category="HTML feature";;
          * ) cat=html/elements; category="HTML element";;
        esac;;
      [Tt*] ) cat=http/headers; category="HTTP feature";;
      [Jj*] ) read -n 1 -p "Sub-category? ([B]uiltins/[o]perators/o[t]her) " subcat;
        echo "";
        case $subcat in
          [Oo*] ) cat=javascript/operators; category="JavaScript operator";;
          [Tt*] ) cat=javascript; category="JavaScript feature";;
          * ) cat=javascript/builtins; category="JavaScript builtin";;
        esac;;
      [Ss*] ) read -n 1 -p "Sub-category? ([a]ttributes/[E]lements) " subcat;
        echo "";
        case $subcat in
          [Aa*] ) cat=svg/attributes; category="SVG attributes";;
          * ) cat=svg/elements; category="SVG element";;
        esac;;
      [Dd*] ) cat=webdriver; category="Webdriver feature";;
      [Ee*] ) cat=webextensions; category="Webextensions feature";;
      * ) cat=api; category=API;;
    esac;;
esac;
case $prtype in
  [NnFfEe*] ) ;;
  [Rr*] )
    read -n 1 -p "Removal reason: ([I]rrelevant/[n]on-interface/[o]ther) " removalreason;
    [[ ! -z $removalreason ]] && echo "";
    case $removalreason in
      [Oo*] ) read -p "Reason: " reason;;
      *) ;;
    esac;
    read -n 1 -p "Does this need an MDN content update? ([Y]es/[n]o) " needscontentupdate;
    [[ ! -z $needscontentupdate ]] && echo "";;
  [Ll*] ) read -p "Flag: " flag;;
  * ) echo "Browser: "; select browseropt in Chromium Edge Firefox IE "IE/Edge" Opera Safari "Safari iOS" "Chrome/Safari" WebView "Firefox Android" "all browsers"; do
    case $browseropt in
      "Chromium") browserid=chrome; browser="Chromium (Chrome, Opera, Samsung Internet, WebView Android)"; break;;
      "Edge") browserid=edge; browser="Microsoft Edge"; break;;
      "Firefox") browserid=firefox; browser="Firefox and Firefox Android"; break;;
      "IE") browserid=ie; browser="Internet Explorer"; break;;
      "IE/Edge") browserid=ms; browser="Internet Explorer and Edge"; break;;
      "Opera") browserid=opera; browser="Opera and Opera Android"; break;;
      "Safari") browserid=safari; browser="Safari (Desktop and iOS/iPadOS)"; break;;
      "Safari iOS") browserid=safariios; browser="Safari iOS/iPadOS"; break;;
      "Chrome/Safari") browserid=webkit; browser="Chrome and Safari"; break;;
      "WebView") browserid=webview; browser="WebView Android"; break;;
      "NodeJS") browserid=nodejs; browser="NodeJS"; break;;
      "Firefox Android") browserid=fenix; browser="Firefox Android"; break;;
      "all browsers") browserid="all"; browser="all browsers"; break;;
    esac;
  done;
  case $prtype in
    [RrLlAaEe*] ) ;;
    * ) read -n 1 -p "Method? (mdn-bcd-collecto[R]/[m]anual/m[i]rror/[c]ommit/[b]ug/[o]ther) " method
      [[ ! -z $method ]] && echo ""
      case $method in 
        [Cc*] ) read -p "Commit: " commit;;
        [Mm*] ) read -p "Test Code/Page (leave blank to link collector): " testcode;;
        [Bb*] )
          case $browserid in
            chrome|opera|webview) read -p "Chromium Bug ID: " bugid; bug="https://crbug.com/${bugid}";;
            firefox) read -p "Bugzilla Bug ID: " bugid; bug="https://bugzil.la/${bugid}";;
            safari|safariios|webkit) read -p "WebKit Bug ID: " bugid; bug="https://webkit.org/b/${bugid}";;
            *) read -p "Bug Link: " bug;;
          esac;;
        [Oo*] ) read -p "Reason: " reason;;
      esac;;
  esac;;
esac;
case $prtype in
  [Ll*] ) doadd=n;
    echo ""
    npm run lint $cat
    if [ $? -ne 0 ]; then
      echo ""
      read -n 1 -s -r -p "Resolve linter issues, then press any key to continue"
      echo ""
    fi;;
  * ) read -p "$category: " feature
    case $prtype in
      [Ff*] ) ;;
      [Ee*] ) read -p "Event name (if applicable): " member;;
      * ) read -p "Member (if applicable): " member;;
    esac;
    read -n 1 -p "Auto-add files? ([Y]es/[n]o) " doadd
    [[ ! -z $doadd ]] && echo ""
    echo ""
    npm run lint $cat/$feature.json
    if [ $? -ne 0 ]; then
      echo ""
      read -n 1 -s -r -p "Resolve linter issues, then press any key to continue"
      echo ""
    fi;;
esac;
case $prtype in
  [Ff*] ) branch=$cat/${feature//\*/};;
  [Nn*] ) if [ -z $member ]; then
    branch=$cat/${feature//\*/}/additions;
  else
    branch=$cat/${feature//\*/}/${member//./\/}/additions;
  fi;;
  [Cc*] ) if [ -z $member ]; then
    branch=$cat/${feature//\*/}/$browserid-corrections;
  else
    branch=$cat/${feature//\*/}/${member//./\/}/$browserid-corrections;
  fi;;
  [Ll*] ) branch=$cat/$flag-flagremoval;;
  [Aa*] ) if [ -z $member ]; then
    branch=$cat/${feature//\*/}/$browserid-flagremoval;
  else
    branch=$cat/${feature//\*/}/${member//./\/}/$browserid-flagremoval;
  fi;;
  [Rr*] ) if [ -z $member ]; then
    branch=$cat/${feature//\*/}/removal;
  else
    branch=$cat/${feature//\*/}/${member//./\/}/removal;
  fi;;
  [Ee*] ) if [ -z $member ]; then
    branch=$cat/${feature//\*/}/events;
  else
    branch=$cat/${feature//\*/}/${member//./\/}/events;
  fi;;
  * ) if [ -z $member ]; then
    branch=$cat/${feature//\*/}/$browserid;
  else
    branch=$cat/${feature//\*/}/${member//./\/}/$browserid;
  fi;;
esac;
git branch $branch -q
git checkout $branch -q
case $doadd in
  [Nn*] ) ;;
  * ) git add $cat/$feature.json;;
esac;
if [ -z $member ]; then
  title="$feature $category"
else
  title="${cat//\//.}.$feature.$member"
fi

if [ -z $member ] || [ $member == "worker_support" ]; then
  collectorurl=https://mdn-bcd-collector.appspot.com/tests/$cat/$feature;
else
  collectorurl=https://mdn-bcd-collector.appspot.com/tests/$cat/$feature/$member;
fi;

case $method in
  [Cc*]) if [ -z $member ]; then
    git commit -m "Add $browseropt versions for $title" -m "" -m "This PR adds real values for $browser for the \`$feature\` $category, based upon commit history and date." -m "" -m "Commit: $commit" -q
  else
    git commit -m "Add $browseropt versions for $title" -m "" -m "This PR adds real values for $browser for the \`$member\` member of the \`$feature\` $category, based upon commit history and date." -m "" -m "Commit: $commit" -q
  fi;;
  [Mm*])
    case "$testcode" in
      http*) ;;
      "") testcode=$collectorurl;;
      *) testcode="\`$testcode\`";;
    esac;

    if [ -z $member ]; then
      git commit -m "Add $browseropt versions for $title" -m "" -m "This PR adds real values for $browser for the \`$feature\` $category, based upon manual testing." -m "" -m "Test Code Used: $testcode" -q
    else
      git commit -m "Add $browseropt versions for $title" -m "" -m "This PR adds real values for $browser for the \`$member\` member of the \`$feature\` $category, based upon manual testing." -m "" -m "Test Code Used: $testcode" -q
    fi;;
  [Ii*])
    if [ -z $member ]; then
      git commit -m "Add $browseropt versions for $title" -m "" -m "This PR adds real values for $browser for the \`$feature\` $category by mirroring the data." -q
    else
      git commit -m "Add $browseropt versions for $title" -m "" -m "This PR adds real values for $browser for the \`$member\` member of the \`$feature\` $category by mirroring the data." -q
    fi;;
  [Bb*]) if [ -z $member ]; then
    git commit -m "Add $browseropt versions for $title" -m "" -m "This PR adds real values for $browser for the \`$feature\` $category, based upon information in a tracking bug." -m "" -m "Tracking Bug: $bug" -q
  else
    git commit -m "Add $browseropt versions for $title" -m "" -m "This PR adds real values for $browser for the \`$member\` member of the \`$feature\` $category, based upon information in a tracking bug." -m "" -m "Tracking Bug: $bug" -q
  fi;;
  [Ww*]) if [ -z $member ]; then
    git commit -m "Add $browseropt versions for $title" -m "" -m "This PR adds real values for $browser for the \`$feature\` $category, based upon results from WPT.fyi." -m "" -m "Test Used: $link" -q
  else
    git commit -m "Add $browseropt versions for $title" -m "" -m "This PR adds real values for $browser for the \`$member\` member of the \`$feature\` $category, based upon results from WPT.fyi." -m "" -m "Test Used: $link" -q
  fi;;
  [Oo*])
    if [ -z $member ]; then
      git commit -m "Add $browseropt versions for $title" -m "" -m "This PR adds real values for $browser for the \`$feature\` $category.  $reason" -q
    else
      git commit -m "Add $browseropt versions for $title" -m "" -m "This PR adds real values for $browser for the \`$member\` member of the \`$feature\` $category.  $reason" -q
    fi;;
  *) case $prtype in
    [Nn*] ) 
      if [ -z $member ]; then
        git commit -m "Add missing features for $title" -m "" -m "This PR is a part of a project to add missing interfaces and interface features to BCD that are from an active spec (including WICG specs) and is supported in at least one browser.  This particular PR adds the missing features of the $feature $category, populating the results using data from the [mdn-bcd-collector](https://mdn-bcd-collector.appspot.com) project (v$collectorversion)." -m "" -m "Tests Used: $collectorurl" -m "" -m "_Check out the [collector's guide on how to review this PR](https://github.com/foolip/mdn-bcd-collector#reviewing-bcd-changes)._" -q
      else
        git commit -m "Add missing $title feature" -m "" -m "This PR is a part of a project to add missing interfaces and interface features to BCD that are from an active spec (including WICG specs) and is supported in at least one browser.  This particular PR adds the missing \`$member\` member of the $feature $category, populating the results using data from the [mdn-bcd-collector](https://mdn-bcd-collector.appspot.com) project (v$collectorversion)." -m "" -m "Tests Used: $collectorurl" -m "" -m "_Check out the [collector's guide on how to review this PR](https://github.com/foolip/mdn-bcd-collector#reviewing-bcd-changes)._" -q
      fi;;
    [Ff*] ) git commit -m "Add missing $title" -m "" -m "This PR is a part of a project to add missing interfaces and interface features to BCD that are from an active spec (including WICG specs) and is supported in at least one browser.  This particular PR adds the missing \`$feature\` $category, populating the results using data from the [mdn-bcd-collector](https://mdn-bcd-collector.appspot.com) project (v$collectorversion)." -m "" -m "Tests Used: $collectorurl" -m "" -m "_Check out the [collector's guide on how to review this PR](https://github.com/foolip/mdn-bcd-collector#reviewing-bcd-changes)._" -q;;
    [Cc*] ) if [ -z $member ]; then
      git commit -m "Update $browseropt versions for $title" -m "" -m "This PR updates and corrects the real values for $browser for the \`$feature\` $category, based upon results from the [mdn-bcd-collector](https://mdn-bcd-collector.appspot.com) project (v$collectorversion)." -m "" -m "Tests Used: $collectorurl" -m "" -m "_Check out the [collector's guide on how to review this PR](https://github.com/foolip/mdn-bcd-collector#reviewing-bcd-changes)._" -q;
      else
        git commit -m "Update $browseropt versions for $title" -m "" -m "This PR updates and corrects the real values for $browser for the \`$member\` member of the \`$feature\` $category, based upon results from the [mdn-bcd-collector](https://mdn-bcd-collector.appspot.com) project (v$collectorversion)." -m "" -m "Tests Used: $collectorurl" -m "" -m "_Check out the [collector's guide on how to review this PR](https://github.com/foolip/mdn-bcd-collector#reviewing-bcd-changes)._" -q;
      fi;;
    [Rr*] ) case $removalreason in
      [Nn*] ) if [ -z $member ]; then
        git commit -m "Remove $title from BCD" -m "" -m "This PR removes \`$feature\` from BCD.  This feature is a dictionary, enum, or WebIDL typedef and should not be included in BCD." -q
      else
        git commit -m "Remove $title from BCD" -m "" -m "This PR removes the \`$member\` member of the \`$feature\` $category from BCD.  This feature is a dictionary, enum, or WebIDL typedef and should not be included in BCD." -q
      fi;;
      [Oo*] ) if [ -z $member ]; then
        git commit -m "Remove $title from BCD" -m "" -m "This PR removes \`$feature\` from BCD.  $reason" -q
      else
        git commit -m "Remove $title from BCD" -m "" -m "This PR removes the \`$member\` member of the \`$feature\` $category from BCD.  $reason" -q
      fi;;
      * ) if [ -z $member ]; then
        git commit -m "Remove $title from BCD" -m "" -m "This PR removes the irrelevant \`$feature\` $category as per the corresponding [data guidelines](https://github.com/mdn/browser-compat-data/blob/main/docs/data-guidelines.md#removal-of-irrelevant-features). The lack of current support has been confirmed by the [mdn-bcd-collector](https://mdn-bcd-collector.appspot.com) project (v$collectorversion), even if the current BCD suggests support." -q;
      else
        git commit -m "Remove $title from BCD" -m "" -m "This PR removes the irrelevant \`$member\` member of the \`$feature\` $category as per the corresponding [data guidelines](https://github.com/mdn/browser-compat-data/blob/main/docs/data-guidelines.md#removal-of-irrelevant-features). The lack of current support has been confirmed by the [mdn-bcd-collector](https://mdn-bcd-collector.appspot.com) project (v$collectorversion), even if the current BCD suggests support." -q;
      fi;;
    esac;;
    [Ll*] ) git commit -m "Remove irrelevant \"$flag\" flag" -m "" -m "This PR removes irrelevant flag data for \`$flag\` as per the corresponding [data guidelines](https://github.com/mdn/browser-compat-data/blob/main/docs/data-guidelines.md#removal-of-irrelevant-flag-data)." -m "" -m "This PR was created from results of a [script](https://github.com/queengooborg/browser-compat-data/blob/scripts/remove-redundant-flags/scripts/remove-redundant-flags.js) designed to remove irrelevant flags." -q;;
    [Aa*] ) if [ -z $member ]; then
      git commit -m "Remove irrelevant $browseropt flag data for $title" -m "" -m "This PR removes irrelevant flag data for $browser for the \`$feature\` $category as per the corresponding [data guidelines](https://github.com/mdn/browser-compat-data/blob/main/docs/data-guidelines.md#removal-of-irrelevant-flag-data)." -m "" -m "This PR was created from results of a [script](https://github.com/queengooborg/browser-compat-data/blob/scripts/remove-redundant-flags/scripts/remove-redundant-flags.js) designed to remove irrelevant flags." -q;
    else
      git commit -m "Remove irrelevant $browseropt flag data for $title" -m "" -m "This PR removes irrelevant flag data for $browser for the \`$member\` member of the \`$feature\` $category as per the corresponding [data guidelines](https://github.com/mdn/browser-compat-data/blob/main/docs/data-guidelines.md#removal-of-irrelevant-flag-data)." -m "" -m "This PR was created from results of a [script](https://github.com/queengooborg/browser-compat-data/blob/scripts/remove-redundant-flags/scripts/remove-redundant-flags.js) designed to remove irrelevant flags." -q;
    fi;;
    [Ee*] ) if [ -z $member ]; then
      git commit -m "Adapt $title to new events structure" -m "" -m "This PR adapts the $feature $category to conform to the new events structure." -q;
    else
      git commit -m "Adapt $title to new events structure" -m "" -m "This PR adapts the $member event of the $feature $category to conform to the new events structure." -q;
    fi;;
    * ) if [ -z $member ]; then
      case $browseropt in
        "WebView") git commit -m "Add $browseropt versions for $title" -m "" -m "This PR adds real values for $browser for the \`$feature\` $category, based upon results from the [mdn-bcd-collector](https://mdn-bcd-collector.appspot.com) project (v$collectorversion).  The collector obtains results based upon the latest WebView version (to determine if it is supported), then version numbers are copied from Chrome Android." -m "" -m "Tests Used: $collectorurl" -m "" -m "_Check out the [collector's guide on how to review this PR](https://github.com/foolip/mdn-bcd-collector#reviewing-bcd-changes)._" -q;;
        "Opera") git commit -m "Add $browseropt versions for $title" -m "" -m "This PR adds real values for $browser for the \`$feature\` $category, based upon results from the [mdn-bcd-collector](https://mdn-bcd-collector.appspot.com) project (v$collectorversion).  The collector obtains results based upon Opera Desktop 12.16 and 15, as well as the latest version of Opera Desktop and Opera Android.  Version numbers are then copied for Blink-based Opera versions from Chrome Desktop and Android respectively." -m "" -m "Tests Used: $collectorurl" -m "" -m "_Check out the [collector's guide on how to review this PR](https://github.com/foolip/mdn-bcd-collector#reviewing-bcd-changes)._" -q;;
        *) git commit -m "Add $browseropt versions for $title" -m "" -m "This PR adds real values for $browser for the \`$feature\` $category, based upon results from the [mdn-bcd-collector](https://mdn-bcd-collector.appspot.com) project (v$collectorversion)." -m "" -m "Tests Used: $collectorurl" -m "" -m "_Check out the [collector's guide on how to review this PR](https://github.com/foolip/mdn-bcd-collector#reviewing-bcd-changes)._" -q;;
      esac;
    else
      case $browseropt in
        "WebView") git commit -m "Add $browseropt versions for $title" -m "" -m "This PR adds real values for $browser for the \`$member\` member of the \`$feature\` $category, based upon results from the [mdn-bcd-collector](https://mdn-bcd-collector.appspot.com) project (v$collectorversion).  The collector obtains results based upon the latest WebView version (to determine if it is supported), then version numbers are copied from Chrome Android." -m "" -m "Tests Used: $collectorurl" -m "" -m "_Check out the [collector's guide on how to review this PR](https://github.com/foolip/mdn-bcd-collector#reviewing-bcd-changes)._" -q;;
        "Opera") git commit -m "Add $browseropt versions for $title" -m "" -m "This PR adds real values for $browser for the \`$member\` member of the \`$feature\` $category, based upon results from the [mdn-bcd-collector](https://mdn-bcd-collector.appspot.com) project (v$collectorversion).  The collector obtains results based upon Opera Desktop 12.16 and 15, as well as the latest version of Opera Desktop and Opera Android.  Version numbers are then copied for Blink-based Opera versions from Chrome Desktop and Android respectively." -m "" -m "Tests Used: $collectorurl" -m "" -m "_Check out the [collector's guide on how to review this PR](https://github.com/foolip/mdn-bcd-collector#reviewing-bcd-changes)._" -q;;
        *) git commit -m "Add $browseropt versions for $title" -m "" -m "This PR adds real values for $browser for the \`$member\` member of the \`$feature\` $category, based upon results from the [mdn-bcd-collector](https://mdn-bcd-collector.appspot.com) project (v$collectorversion)." -m "" -m "Tests Used: $collectorurl" -m "" -m "_Check out the [collector's guide on how to review this PR](https://github.com/foolip/mdn-bcd-collector#reviewing-bcd-changes)._" -q;;
      esac;
    fi;;
  esac;
esac;
case $prtype in
  [Rr*] ) case $needscontentupdate in
    [Nn*] ) gh pr create --fill -l "needs-release-note :newspaper:";;
    * ) gh pr create --fill -l "needs-release-note :newspaper:" -l "needs content update 📝";;
  esac;;
  [Ee*] ) gh pr create --fill -l "needs content update 📝";;
  * ) gh pr create --fill;;
esac;
case $doadd in
  [NnCc*] ) git stash;;
esac;
git checkout main -q
git branch -d $branch -q
case $doadd in
  [NnCc*] ) git stash pop -q; git reset -q;;
esac;
