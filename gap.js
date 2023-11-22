function a2m(array, h, w){
    let matrix = [];
    for(let y = 0; y < h; y++){
        let row = array.slice(y * w * 4,(y + 1) * w * 4);
        let convertedRow = [];
        for(let step = 0; step < row.length; step += 4){
            convertedRow.push([row[step],row[step + 1],row[step + 2],row[step + 3]])
        }
        matrix.push(convertedRow)
    }
    return matrix
}

function m2a(matrix){
    let array = [];
    for(let y = 0; y < matrix.length; y++){
        for(let x = 0; x < matrix[y].length; x++){
            array.push(...matrix[y][x]);
        }
    }
    return new Uint8ClampedArray(array);
}

function pixelIsWhite(p){
    return p[0] + p[1] + p[2] === 255 * 3
}

function solve(p,w,h){
    var pixels = Uint8ClampedArray.from(p)
    var w = w;
    var h = h;
    var matrix = a2m(pixels, h, w);
    var deltaMatrix = [];
    for(let y = 0; y < matrix.length; y++){
        let row = matrix[y];
        deltaMatrix[y] = new Array(row.length);
        // first pixel will be empty
        deltaMatrix[y][0] = [0,0,0,0];
        for(let x = 1; x < row.length; x++){
            let p0 = row[x -1]; // previous pixel
            let p1 = row[x];    // current pixel
            // gray scale:
            let baw = true; // turn black and white?
            let avg = (Math.abs(p0[0] - p1[0]) + Math.abs(p0[1] - p1[1]) + Math.abs(p0[2] - p1[2])) / 3;
            // noise filter
            let minLevel = 70;
            if(avg < minLevel){avg = 0;}
            else if(baw){avg = 255;}
            let p2 = [255 - avg,255 - avg,255 - avg,255];
            // end gray
            deltaMatrix[y][x] = p2;
        }
    }
    var streaks = [];
    for(let y = 1; y < h; y++){
        for(let x = 0; x < w; x++){
            let p0 = deltaMatrix[y - 1][x];
            let p1 = deltaMatrix[y][x];
            if(pixelIsWhite(p1)){continue;}
            if(pixelIsWhite(p0)){deltaMatrix[y][x] = [255,0,0,255];}
            for(let streak = 0; true; streak++){
                let y2 = y + streak; // the y-coordinate to test
                // check if pixel is out of bounds
                if(!deltaMatrix[y2]){break;}
                if(pixelIsWhite(deltaMatrix[y2][x])){ // end streak
                    deltaMatrix[y2 - 1][x] = [0,0,255,255];
                    streaks.push({length: streak,x: x,y: y});
                    break;
                }
            }
        }
    }
    // sort streaks by length high -> low
    streaks = streaks.sort((a,b)=>{
        return b.length - a.length
    });
    let s = streaks[0];
    return s.x
}