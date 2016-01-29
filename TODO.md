Known bugs:
- key path on schema reporting is always wrong

Actual friend looking for:
- Sum types (kind of already there)
- matching/case clauses on sum types
   can do a call like this (javascript api):

      const Either(e,a) = new Sum({Left: e, Right: a});
      const {Left, Right} = Either

      const either = (l, r, v) => v.match({
          Left:  (x) => onLeft(l),
            Right: (x) => onRight(r),
      });

      either(id, id, Left(9)) // 9

      either instanceOf Either === true

I'm thinking of:
- alias types!  I.e., you can do ItemId = Int,
   and then ItemId type would only validate against other ItemId declarations.
   Not sure this is possible!
