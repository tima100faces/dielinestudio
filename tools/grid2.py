from extract_paths import run
cut,cre=run('samples/ref_14747.pdf'); recs=cut+cre
V=[]
for r in recs:
    for a,b in zip(r['pts'],r['pts'][1:]):
        (x1,y1),(x2,y2)=a,b
        if abs(x1-x2)<0.4 and abs(y1-y2)>2: V.append((round((x1+x2)/2,1),abs(y1-y2)))
def cl(vals,tol=1.2):
    vals=sorted(vals);out=[];g=[vals[0]]
    for v in vals[1:]:
        if v-g[-1]<=tol:g.append(v)
        else:out.append(g);g=[v]
    out.append(g);return [round(sum(z)/len(z),1) for z in out]
# only "long" verticals (real folds, len>40) to ignore tabs/teeth
longV=[v for v in V if v[1]>40]
cx=cl([v[0] for v in longV])
print("LONG vertical folds x:",cx)
print("spacings:",[round(b-a,1) for a,b in zip(cx,cx[1:])])
allx=cl([v[0] for v in V])
print("\nALL vertical x:",allx)
print("spacings:",[round(b-a,1) for a,b in zip(allx,allx[1:])])
